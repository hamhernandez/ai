FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# 1. Dependencias del sistema
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    tzdata \
    python3-pip \
    git ffmpeg libgl1-mesa-glx python3-opencv \
    openssh-server sudo \
    && ln -fs /usr/share/zoneinfo/Europe/Madrid /etc/localtime \
    && dpkg-reconfigure --frontend noninteractive tzdata \
    && pip3 install --upgrade pip \
    && rm -rf /var/lib/apt/lists/*

# 2. Instalar PyTorch manualmente
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 3. Configurar usuario y SSH
RUN useradd -m runpod && echo 'runpod ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
RUN mkdir /var/run/sshd

# 4. Copiar clave pública
COPY keys/id_rsa.pub /home/runpod/.ssh/authorized_keys
RUN chown -R runpod:runpod /home/runpod/.ssh \
    && chmod 700 /home/runpod/.ssh \
    && chmod 600 /home/runpod/.ssh/authorized_keys

# 5. Configurar SSH seguro
RUN sed -i 's/^#*Port .*/Port 2222/' /etc/ssh/sshd_config \
    && sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config \
    && sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config

# 6. Clonar e instalar Hunyuan + descargar pesos pre-entrenados
WORKDIR /workspace
RUN git clone https://github.com/Tencent/HunyuanVideo.git \
    && cd HunyuanVideo \
    && git submodule update --init --recursive \
    && pip install -r requirements.txt \
    && pip install "huggingface_hub[cli]" \
    && huggingface-cli download tencent/HunyuanVideo --local-dir ./ckpts

# 7. Entrypoint
COPY entrypoint.sh /workspace/entrypoint.sh
RUN chmod +x /workspace/entrypoint.sh

# 8. Exponer puertos necesarios
EXPOSE 2222 7860

ENTRYPOINT ["/workspace/entrypoint.sh"]