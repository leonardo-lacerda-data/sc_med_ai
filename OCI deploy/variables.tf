variable "tenancy_ocid" {}
variable "region" {}
variable "compartment_ocid" {}
variable "ssh_public_key" {}

variable "AD" {
  default = "1"
}

variable "vcn_ocid" {
  description = ""
  type        = string
}

variable "subnet_cidr" {
  description = ""
  type        = string
  default     = "10.0.10.0/24"
}

variable "image_operating_system" {
  default = "Canonical Ubuntu"
}

variable "image_operating_system_version" {
  default = "24.04"
}

variable "instance_shape" {
  description = "Instance Shape"
  default     = "VM.Standard.E2.1.Micro"
}

variable "instance_count" {
  description = "Instâncias de aplicação atrás do Load Balancer"
  type        = number
  default     = 2
}

variable "load_balancer_min_band" {
  description = "Load Balancer Min Band"
  default     = "10"
}

variable "load_balancer_max_band" {
  description = "Load Balancer Max Band"
  default     = "10"
}

variable "cert_passphrase" {
  description = "Senha do certificado SSL"
  type        = string
  sensitive   = true
  default     = ""
}

variable "app_bundle_url" {
  description = "URL do pacote .zip da aplicação no Object Storage"
  type        = string
}

variable "google_api_key" {
  description = "Chave da API do Gemini"
  type        = string
  sensitive   = true
}

variable "gemini_chat_model" {
  description = "Modelo de geração"
  type        = string
  default     = "gemini-2.5-flash"
}

variable "gemini_embedding_model" {
  description = "Modelo de embeddings"
  type        = string
  default     = "gemini-embedding-001"
}
