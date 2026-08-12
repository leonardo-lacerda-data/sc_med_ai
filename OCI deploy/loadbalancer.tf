resource "oci_load_balancer_load_balancer" "Load_Balancer" {
  compartment_id = var.compartment_ocid
  display_name   = "scmedai-lb"
  shape          = "flexible"
  subnet_ids = [
    oci_core_subnet.public_subnet.id,
  ]
  shape_details {
    maximum_bandwidth_in_mbps = var.load_balancer_max_band
    minimum_bandwidth_in_mbps = var.load_balancer_min_band
  }
}

resource "oci_load_balancer_backend_set" "web-servers-backend" {
  load_balancer_id = oci_load_balancer_load_balancer.Load_Balancer.id
  name             = "web-servers-backend"
  policy           = "ROUND_ROBIN"

  session_persistence_configuration {
    cookie_name      = "X-Oracle-BMC-LBS-Route"
    disable_fallback = false
  }

  health_checker {
    interval_ms         = "10000"
    port                = "80"
    protocol            = "HTTP"
    response_body_regex = ""
    retries             = "3"
    return_code         = "200"
    timeout_in_millis   = "3000"
    url_path            = "/_stcore/health"
  }
}

resource "oci_load_balancer_backend" "app" {
  count = var.instance_count

  backendset_name  = oci_load_balancer_backend_set.web-servers-backend.name
  load_balancer_id = oci_load_balancer_load_balancer.Load_Balancer.id
  ip_address       = oci_core_instance.app[count.index].private_ip
  port             = "80"
  backup           = "false"
  drain            = "false"
  offline          = "false"
  weight           = "1"
}

resource "oci_load_balancer_listener" "lb-listener-http" {
  connection_configuration {
    idle_timeout_in_seconds = "300"
  }
  default_backend_set_name = oci_load_balancer_backend_set.web-servers-backend.name
  load_balancer_id         = oci_load_balancer_load_balancer.Load_Balancer.id
  name                     = "lb-listener-http"
  port                     = "80"
  protocol                 = "HTTP"
}
