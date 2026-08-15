locals {
  user_data = templatefile("${path.module}/cloud-init.yaml", {
    app_source_url         = var.app_source_url
    google_api_key         = var.google_api_key
    gemini_chat_model      = var.gemini_chat_model
    gemini_embedding_model = var.gemini_embedding_model
  })
}

resource "oci_core_instance" "app" {
  count = var.instance_count

  availability_domain = data.oci_identity_availability_domains.ADs.availability_domains[var.AD - 1]["name"]
  compartment_id      = var.compartment_ocid
  display_name        = "scmedai-app-${count.index + 1}"
  shape               = var.instance_shape

  create_vnic_details {
    subnet_id    = oci_core_subnet.public_subnet.id
    display_name = "scmedai-app-${count.index + 1}-vnic1"
  }

  source_details {
    source_type             = "image"
    source_id               = lookup(data.oci_core_images.compute_images.images[0], "id")
    boot_volume_size_in_gbs = "50"
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
    user_data           = base64encode(local.user_data)
  }
}
