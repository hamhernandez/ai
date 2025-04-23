FROM pytorch/pytorch:2.0.1-cuda11.8-cudnn8-runtime

# 1. Instala dependencias necesarias
RUN apt-get update && apt-get install -y \
    git git-lfs ffmpeg libgl1-mesa-glx python3-opencv \
    openssh-server sudo \
 && git lfs install \
 && rm -rf /var/lib/apt/lists/*

# 2. Prepara SSH
RUN mkdir /var/run/sshd

# 3. Crea usuario con acceso sudo sin contraseña
RUN useradd -m runpod && echo 'runpod ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# 4. Prepara carpeta SSH y copia tu clave pública
RUN mkdir -p /home/runpod/.ssh
COPY keys/id_rsa.pub /home/runpod/.ssh/authorized_keys
RUN chown -R runpod:runpod /home/runpod/.ssh \
    && chmod 700 /home/runpod/.ssh \
    && chmod 600 /home/runpod/.ssh/authorized_keys

# 5. Configura SSH
RUN sed -i 's/^#*Port .*/Port 2222/' /etc/ssh/sshd_config \
    && sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config \
    && sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config \
    && echo "PubkeyAuthentication yes" >> /etc/ssh/sshd_config

# 6. Exponemos puertos necesarios
EXPOSE 2222 7860

# 7. Clona e instala Hunyuan Video
WORKDIR /workspace
RUN git clone https://github.com/Tencent/HunyuanVideo.git \
    && cd HunyuanVideo \
    && git submodule update --init --recursive \
    && pip install --no-cache-dir -r requirements.txt

# 8. Copia y da permiso al script de entrada
COPY entrypoint.sh /workspace/entrypoint.sh
RUN chmod +x /workspace/entrypoint.sh

ENTRYPOINT ["/workspace/entrypoint.sh"]

# 9. Opcional: línea para debug manual si no se usa entrypoint
# CMD ["/usr/sbin/sshd", "-D"]