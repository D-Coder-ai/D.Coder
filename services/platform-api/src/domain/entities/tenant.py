"""
Tenant Entity - Core Domain Model
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from enum import Enum


class TenantStatus(Enum):
    """Tenant status enumeration"""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class TenantTier(Enum):
    """Tenant subscription tier"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class Tenant:
    """
    Tenant entity representing an organization using the platform

    This is a pure domain model with no framework dependencies
    """
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    slug: str = ""
    status: TenantStatus = TenantStatus.PENDING
    tier: TenantTier = TenantTier.FREE

    # Organization details
    organization_name: str = ""
    organization_domain: Optional[str] = None
    organization_size: Optional[str] = None

    # Contact information
    primary_contact_email: str = ""
    primary_contact_name: Optional[str] = None
    billing_email: Optional[str] = None

    # Configuration
    settings: Dict[str, Any] = field(default_factory=dict)
    features: List[str] = field(default_factory=list)

    # Quotas
    max_users: int = 10
    max_requests_per_month: int = 10000
    max_storage_gb: int = 10

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    activated_at: Optional[datetime] = None
    suspended_at: Optional[datetime] = None

    def __post_init__(self):
        """Post-initialization validation and setup"""
        if not self.slug and self.name:
            self.slug = self._generate_slug(self.name)

        if not self.billing_email:
            self.billing_email = self.primary_contact_email

    def _generate_slug(self, name: str) -> str:
        """Generate URL-safe slug from name"""
        import re
        slug = name.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')

    def activate(self) -> None:
        """Activate the tenant"""
        if self.status != TenantStatus.PENDING:
            raise ValueError(f"Cannot activate tenant in {self.status} status")

        self.status = TenantStatus.ACTIVE
        self.activated_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def suspend(self, reason: Optional[str] = None) -> None:
        """Suspend the tenant"""
        if self.status != TenantStatus.ACTIVE:
            raise ValueError(f"Cannot suspend tenant in {self.status} status")

        self.status = TenantStatus.SUSPENDED
        self.suspended_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

        if reason:
            self.settings["suspension_reason"] = reason

    def reactivate(self) -> None:
        """Reactivate a suspended tenant"""
        if self.status != TenantStatus.SUSPENDED:
            raise ValueError(f"Cannot reactivate tenant in {self.status} status")

        self.status = TenantStatus.ACTIVE
        self.suspended_at = None
        self.updated_at = datetime.utcnow()

        # Remove suspension reason if exists
        self.settings.pop("suspension_reason", None)

    def archive(self) -> None:
        """Archive the tenant (soft delete)"""
        if self.status == TenantStatus.ARCHIVED:
            raise ValueError("Tenant is already archived")

        self.status = TenantStatus.ARCHIVED
        self.updated_at = datetime.utcnow()

    def update_tier(self, new_tier: TenantTier) -> None:
        """Update tenant subscription tier"""
        if self.status != TenantStatus.ACTIVE:
            raise ValueError(f"Cannot update tier for tenant in {self.status} status")

        old_tier = self.tier
        self.tier = new_tier
        self.updated_at = datetime.utcnow()

        # Update quotas based on tier
        if new_tier == TenantTier.FREE:
            self.max_users = 10
            self.max_requests_per_month = 10000
            self.max_storage_gb = 10
        elif new_tier == TenantTier.PRO:
            self.max_users = 50
            self.max_requests_per_month = 100000
            self.max_storage_gb = 100
        elif new_tier == TenantTier.ENTERPRISE:
            self.max_users = -1  # Unlimited
            self.max_requests_per_month = -1  # Unlimited
            self.max_storage_gb = 1000

        # Log tier change
        self.settings["tier_history"] = self.settings.get("tier_history", [])
        self.settings["tier_history"].append({
            "from": old_tier.value,
            "to": new_tier.value,
            "changed_at": datetime.utcnow().isoformat()
        })

    def add_feature(self, feature: str) -> None:
        """Add a feature to the tenant"""
        if feature not in self.features:
            self.features.append(feature)
            self.updated_at = datetime.utcnow()

    def remove_feature(self, feature: str) -> None:
        """Remove a feature from the tenant"""
        if feature in self.features:
            self.features.remove(feature)
            self.updated_at = datetime.utcnow()

    def has_feature(self, feature: str) -> bool:
        """Check if tenant has a specific feature"""
        return feature in self.features

    def is_quota_exceeded(self, quota_type: str, current_usage: int) -> bool:
        """Check if a quota has been exceeded"""
        quota_map = {
            "users": self.max_users,
            "requests": self.max_requests_per_month,
            "storage": self.max_storage_gb
        }

        max_allowed = quota_map.get(quota_type, 0)
        if max_allowed == -1:  # Unlimited
            return False

        return current_usage >= max_allowed

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "slug": self.slug,
            "status": self.status.value,
            "tier": self.tier.value,
            "organization_name": self.organization_name,
            "organization_domain": self.organization_domain,
            "organization_size": self.organization_size,
            "primary_contact_email": self.primary_contact_email,
            "primary_contact_name": self.primary_contact_name,
            "billing_email": self.billing_email,
            "settings": self.settings,
            "features": self.features,
            "max_users": self.max_users,
            "max_requests_per_month": self.max_requests_per_month,
            "max_storage_gb": self.max_storage_gb,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "activated_at": self.activated_at.isoformat() if self.activated_at else None,
            "suspended_at": self.suspended_at.isoformat() if self.suspended_at else None
        }