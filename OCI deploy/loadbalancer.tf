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

# Certificado SSL (HTTPS) — habilite quando tiver o par de arquivos.
/*resource "oci_load_balancer_certificate" "cert_https" {
  load_balancer_id = oci_load_balancer_load_balancer.Load_Balancer.id
  certificate_name = "cert-scmedai"

  public_certificate = file("${path.module}/certs/cert.pem")
  private_key        = file("${path.module}/certs/key.pem")

  passphrase = var.cert_passphrase
}
*/

resource "oci_load_balancer_backend_set" "web-servers-backend" {
  load_balancer_id = oci_load_balancer_load_balancer.Load_Balancer.id
  name             = "web-servers-backend"
  policy           = "ROUND_ROBIN"

  # O Streamlit é STATEFUL: o estado da conversa vive na memória do
  # processo, não em banco. Sem persistência de sessão, o round-robin
  # manda o usuário para a outra instância e o histórico "some".
  # O cookie emitido pelo próprio balanceador prende cada usuário a um
  # backend enquanto a sessão durar.
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

    # Endpoint de saúde do próprio Streamlit. Melhor que "/": responde
    # rápido, não renderiza a página inteira e não conta como sessão.
    url_path = "/_stcore/health"
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

/*resource "oci_load_balancer_listener" "lb-listener-https" {
  connection_configuration {
    idle_timeout_in_seconds = "300"
  }
  default_backend_set_name = oci_load_balancer_backend_set.web-servers-backend.name
  load_balancer_id         = oci_load_balancer_load_balancer.Load_Balancer.id
  name                     = "lb-listener-https"
  port                     = "443"
  protocol                 = "HTTP"
  ssl_configuration {
    certificate_name        = oci_load_balancer_certificate.cert_https.certificate_name
    verify_peer_certificate = false
    protocols               = ["TLSv1.2"]
  }
}
*/

resource "oci_load_balancer_listener" "lb-listener-http" {
  connection_configuration {
    # O padrão de 60s derruba a conexão WebSocket do Streamlit enquanto o
    # usuário lê a resposta, e a tela volta para "Connecting...".
    idle_timeout_in_seconds = "300"
  }
  default_backend_set_name = oci_load_balancer_backend_set.web-servers-backend.name
  load_balancer_id         = oci_load_balancer_load_balancer.Load_Balancer.id
  name                     = "lb-listener-http"
  port                     = "80"
  protocol                 = "HTTP"
}
