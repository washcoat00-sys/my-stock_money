
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python3
    pkgs.python3Packages.pandas
    pkgs.python3Packages.scipy
    (pkgs.python3Packages.buildPythonPackage rec {
      pname = "pykrx";
      version = "1.2.4";
      format = "pyproject";

      src = pkgs.fetchPypi {
        inherit pname version;
        sha256 = "9ff5415ff7d171fe224b8e1f52531e55e3d0b00adf49234f03acd356ebe451b5";
      };

      nativeBuildInputs = with pkgs.python3Packages; [
        setuptools
        wheel
        setuptools-scm
      ];

      propagatedBuildInputs = with pkgs.python3Packages; [
        requests
        pandas
        numpy
        deprecated
        multipledispatch
        matplotlib
      ];

      doCheck = false;
    })
  ];
}
