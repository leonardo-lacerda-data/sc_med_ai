#!/usr/bin/env bash
# Preparação da instância OCI. Roda UMA vez, na VM, como usuário padrão
# (opc no Oracle Linux, ubuntu no Ubuntu).
#
#   bash setup-vm.sh
#
# Faz: área de troca, Docker, e abertura das portas no firewall do SO.
set -euo pipefail

echo "==> 1/3  Área de troca"
# A instância tem 1 GB e não vem com swap. Sem ele, qualquer pico de
# memória mata o processo — inclusive durante o `docker pull`.
if ! swapon --show | grep -q .; then
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    # Com pouca RAM, vale trocar mais cedo do que o padrão do sistema.
    echo 'vm.swappiness=60' | sudo tee /etc/sysctl.d/99-swap.conf
    sudo sysctl -p /etc/sysctl.d/99-swap.conf
    echo "    swap de 2 GB criado"
else
    echo "    swap já existe, pulando"
fi

echo "==> 2/3  Docker"
if ! command -v docker >/dev/null 2>&1; then
    curl -fsSL https://get.docker.com | sudo sh
    sudo usermod -aG docker "$USER"
    sudo systemctl enable --now docker
    echo "    Docker instalado"
else
    echo "    Docker já instalado, pulando"
fi

echo "==> 3/3  Firewall do sistema operacional"
# ATENÇÃO: liberar a porta na Security List da VCN NÃO basta. As imagens
# da OCI vêm com o firewall do SO bloqueando tudo menos a 22. Esquecer
# este passo produz um sintoma idêntico ao de aplicação fora do ar.
if command -v firewall-cmd >/dev/null 2>&1; then
    sudo firewall-cmd --permanent --add-port=80/tcp
    sudo firewall-cmd --permanent --add-port=443/tcp
    sudo firewall-cmd --reload
    echo "    firewalld liberado (80, 443)"
else
    sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80  -j ACCEPT
    sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
    sudo apt-get install -y iptables-persistent >/dev/null 2>&1 || true
    sudo netfilter-persistent save >/dev/null 2>&1 \
        || sudo sh -c 'iptables-save > /etc/iptables/rules.v4'
    echo "    iptables liberado (80, 443)"
fi

echo
echo "Pronto. SAIA E ENTRE DE NOVO no SSH para o grupo docker valer."
echo "Depois confira:  docker run --rm hello-world"
free -h
