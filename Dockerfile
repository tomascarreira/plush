FROM nixos/nix

RUN mkdir /plus
WORKDIR /plush
ADD . . 

