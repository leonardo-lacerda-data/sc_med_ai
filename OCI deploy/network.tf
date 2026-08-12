data "oci_core_internet_gateways" "igw" {
  compartment_id = var.compartment_ocid
  vcn_id         = var.vcn_ocid
  state          = "AVAILABLE"
}

resource "oci_core_route_table" "public_rt" {
  compartment_id = var.compartment_ocid
  vcn_id         = var.vcn_ocid
  display_name   = "scmedai-public-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    network_entity_id = data.oci_core_internet_gateways.igw.gateways[0].id
  }
}

resource "oci_core_security_list" "sl_public" {
  display_name   = "scmedai-sl-public"
  compartment_id = var.compartment_ocid
  vcn_id         = var.vcn_ocid

  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
  }

  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 80
      max = 80
    }
  }

  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 443
      max = 443
    }
  }

  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 22
      max = 22
    }
  }
}

resource "oci_core_subnet" "public_subnet" {
  compartment_id = var.compartment_ocid
  vcn_id         = var.vcn_ocid
  cidr_block     = var.subnet_cidr

  display_name = "scmedai-public-subnet"
  dns_label    = "scmedai"

  route_table_id             = oci_core_route_table.public_rt.id
  security_list_ids          = [oci_core_security_list.sl_public.id]
  prohibit_public_ip_on_vnic = false
}
