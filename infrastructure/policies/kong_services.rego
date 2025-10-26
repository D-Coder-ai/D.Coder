package kong.services

# Rego v1 syntax
# Deny any service whose URL host is not in the allowlist
violation contains msg if {
  some i
  svc := input.services[i]
  host := host_from_url(svc.url)
  not allowed_host(host)
  msg := sprintf("service '%s' has disallowed host '%s'", [svc.name, host])
}

allowed_host(h) if {
  some j
  allowed := input.allowed_hosts[j]
  h == allowed
}

host_from_url(u) := h if {
  parts := split(u, "://")
  rest := parts[count(parts)-1]
  first := split(rest, "/")[0]
  h := split(first, ":")[0]
}


