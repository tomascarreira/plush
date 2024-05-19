FROM nixos/nix

RUN nix-shell -p git

RUN git clone https://github.com/tomascarreira/plush.git

WORKDIR /plush
