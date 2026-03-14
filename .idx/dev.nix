{ ... }:
{
  # The following specifies a custom channel for nixpkgs.
  # nixpkgs = "https://nixos.org/channels/nixos-23.11/nixexprs.tar.xz";

  # The following installs packages into your workspace.
  # packages = [
  #   pkgs.python3
  #   pkgs.zlib
  #   pkgs.stdenv
  # ];

  # The following starts a process when your workspace starts.
  # processes = {
  #   my-server = {
  #     command = "npm run dev";
  #     autostart = true;
  #   };
  # };

  # The following opens a port in your workspace.
  # ports = {
  #   # "my-port" is a friendly name for the port.
  #   my-port = 3000;
  # };

  # The following previews a file when your workspace starts.
  # preview = {
  #   # "my-file.html" is a file in your workspace.
  #   file = "my-file.html";
  # };
}
