FROM nixos/nix

RUN nix-shell -p python311 python311Packages.ply llvm gcc
