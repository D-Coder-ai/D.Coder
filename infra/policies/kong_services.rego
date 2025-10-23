package kong.services

# Deny any service whose URL host is not in the allowlist
violation[msg] {
  some i
  svc := input.services[i]
  host := host_from_url(svc.url)
  not allowed_host(host)
  msg := sprintf("service '%s' has disallowed host '%s'", [svc.name, host])
}

allowed_host(h) {
  some j
  h == input.allowed_hosts[j]
}

host_from_url(u) = h {
  parts := split(u, "://")
  rest := parts[count(parts)-1]
  first := split(rest, "/")[0]
  h := split(first, ":")[0]
}


