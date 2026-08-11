output "URL_da_aplicacao" {
  description = "Abra este endereço no navegador"
  value       = "http://${oci_load_balancer_load_balancer.Load_Balancer.ip_address_details[0].ip_address}"
}

output "Load_Balancer_Public_IP" {
  value = oci_load_balancer_load_balancer.Load_Balancer.ip_address_details[0].ip_address
}

output "IPs_publicos_das_instancias" {
  description = "Use para SSH e para ler o log do cloud-init"
  value       = oci_core_instance.app[*].public_ip
}

output "Comandos_de_verificacao" {
  value = <<-EOT

    1. Acompanhe o provisionamento (leva ~8 min por causa do pip install):
       ssh ubuntu@<IP-da-instancia>
       sudo tail -f /var/log/cloud-init-output.log

    2. Confira o serviço:
       systemctl status scmedai
       journalctl -u scmedai -n 50 --no-pager

    3. Teste local na instância antes de culpar o balanceador:
       curl -I http://127.0.0.1/_stcore/health

    4. Memória (esta instância tem 1 GB + 2 GB de swap):
       free -h

  EOT
}
