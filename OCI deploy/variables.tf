# Data from terraform.tfvars file

variable "tenancy_ocid" {}
variable "region" {}
variable "compartment_ocid" {}
variable "ssh_public_key" {}

# Choose an Availability Domain
variable "AD" {
  default = "1"
}

# VCN variables
variable "vcn_cidr" {
  default = "10.0.0.0/16"
}

variable "vcn_dns_label" {
  description = "VCN DNS label"
  default     = "scmedai"
}

# OS Image

variable "image_operating_system" {
  default = "Canonical Ubuntu"
}

variable "image_operating_system_version" {
  default = "24.04"
}

### Compute Shape

variable "instance_shape" {
  description = "Instance Shape"
  default     = "VM.Standard.E2.1.Micro"
}

# Load Balancer Shape

variable "load_balancer_min_band" {
  description = "Load Balancer Max Band"
  default     = "10"
}

variable "load_balancer_max_band" {
  description = "Load Balancer Max Band"
  default     = "10"
}

####################################
# Load Balancer
####################################

variable "cert_passphrase" {
  description = "Senha do certificado SSL (deixe vazio se não tiver)"
  type        = string
  sensitive   = true
  default     = ""
}

####################################
# SCMedAI — aplicação
####################################

variable "app_bundle_url" {
  description = <<-EOT
    URL do pacote da aplicação (.zip) no Object Storage.

    O pacote deve conter, na raiz do zip: app.py, src/, prompts/,
    .streamlit/, escudo_header.png, chroma_db/ e requirements-docker.txt.

    Gere um Pre-Authenticated Request (PAR) do objeto no bucket e cole a
    URL aqui. PAR de leitura, com validade que cubra a avaliação.
  EOT
  type        = string
}

variable "google_api_key" {
  description = "Chave da API do Gemini. Gravada em /opt/scmedai/.env com permissão 0600."
  type        = string
  sensitive   = true
}

variable "gemini_chat_model" {
  description = "Modelo de geração"
  type        = string
  default     = "gemini-2.5-flash"
}

variable "gemini_embedding_model" {
  description = "Modelo de embeddings. Precisa ser O MESMO usado para construir o índice."
  type        = string
  default     = "gemini-embedding-001"
}

variable "instance_count" {
  description = "Quantidade de instâncias de aplicação atrás do Load Balancer"
  type        = number
  default     = 2
}
