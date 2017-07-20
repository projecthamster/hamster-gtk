with import <nixpkgs> {};

stdenv.mkDerivation rec {
  name = "env";

  # Mandatory boilerplate for buildable env
  env = buildEnv { name = name; paths = buildInputs; };
  builder = builtins.toFile "builder.sh" ''
    source $stdenv/setup; ln -s $env $out
  '';

  buildInputs = [
    gtk3
    (python35.buildEnv.override {
      ignoreCollisions = true;
      extraLibs = with python35Packages;
        let
          "hamster-gtk" = buildPythonPackage rec {
            name = "hamster-gtk";
            src = ./.;
            doCheck = false;
            buildInputs = [
              gtk3
            ];
            propagatedBuildInputs = [
              hamster-lib
              pygobject3
              orderedset
              six
            ];
            checkInputs = [
              fauxfactory
              freezegun
              pytest
              pytest-faker
              pytest-factoryboy
              pytest-mock
              pytest-xvfb
            ];
            checkPhase = "py.test";
          };
          "hamster-lib" = buildPythonPackage rec {
            pname = "hamster-lib";
            version = "0.13.1";
            name = "${pname}-${version}";
            src = fetchPypi {
              inherit pname version;
              sha256 = "da46bb982c23cf73c5fde171d1d0e66fc1d76b4bab9283dd432b0a43f18c9e21";
            };
            doCheck = false;
            propagatedBuildInputs = [
              sqlalchemy
              appdirs
              configparser
              future
              icalendar
              six
            ];
            checkInputs = [
              pytest
              pytest-faker
              pytest-factoryboy
              fauxfactory
              pytest-mock
              freezegun
            ];
            patchPhase = ''
              sed 's/find_packages()/find_packages(exclude=["tests"])/;s/.*configparser.*//g' -i setup.py
              find tests -type f -exec sed -i 's/backports\.//g' {} +
            '';
          };
          "fauxfactory" = buildPythonPackage rec {
            pname = "fauxfactory";
            version = "2.0.9";
            name = "${pname}-${version}";
            src = fetchPypi {
              inherit pname version;
              sha256 = "a572e99c5cdb7efcec811cfe03cfe7a07cf714d2e74f9ab16848db79b0217a2b";
            };
            doCheck = false;
            propagatedBuildInputs = [ ];
            meta = with stdenv.lib; {
              homepage = "https://github.com/omaciel/fauxfactory";
              license = licenses.asl20;
              description = "Generates random data for your tests.";
            };
          };
          "factory_boy" = buildPythonPackage rec {
            pname = "factory_boy";
            version = "2.8.1";
            name = "${pname}-${version}";
            src = fetchPypi {
              inherit pname version;
              sha256 = "a6644e391a371be603aca8624f3dedbc5a2aa4622878c20494ba17abb4b171bb";
            };
            doCheck = false;
            propagatedBuildInputs = [
              faker
            ];
            meta = with stdenv.lib; {
              homepage = "https://github.com/FactoryBoy/factory_boy";
              license = licenses.mit;
              description = "A versatile test fixtures replacement based on thoughtbot's factory_girl for Ruby.";
            };
          };
          "pytest-factoryboy" = buildPythonPackage rec {
            pname = "pytest-factoryboy";
            version = "1.3.0";
            name = "${pname}-${version}";
            src = fetchPypi {
              inherit pname version;
              sha256 = "2cf4e8af48aa66da367c547e6a59e0b263a87c52e14c59b3197cde4dbcf117a2";
            };
            doCheck = false;
            propagatedBuildInputs = [
              factory_boy
              inflection
              pytest
            ];
            meta = with stdenv.lib; {
              homepage = "https://github.com/pytest-dev/pytest-factoryboy";
              license = licenses.mit;
              description = "Factory Boy support for pytest.";
            };
          };

          "orderedset" = buildPythonPackage rec {
            pname = "orderedset";
            version = "2.0";
            name = "${pname}-${version}";
            src = fetchPypi {
              inherit pname version;
              sha256 = "2a1815512c95ba0bcb73856b74204d4c0998e1fa2fb8a07aec1b666929db933e";
            };
            doCheck = false;
            propagatedBuildInputs = [ ];
            meta = with stdenv.lib; {
              homepage = "https://github.com/simonpercivall/orderedset";
              license = licenses.bsdOriginal;
              description = "An Ordered Set implementation in Cython.";
            };
          };


          "pytest-faker" = buildPythonPackage rec {
            pname = "pytest-faker";
            version = "2.0.0";
            name = "${pname}-${version}";
            src = fetchPypi {
              inherit pname version;
              sha256 = "6b37bb89d94f96552bfa51f8e8b89d32addded8ddb58a331488299ef0137d9b6";
            };
            doCheck = false;
            propagatedBuildInputs = [
              faker
            ];
            meta = with stdenv.lib; {
              homepage = "https://github.com/pytest-dev/pytest-faker";
              license = licenses.mit;
              description = "Faker integration with the pytest framework.";
            };
          };

          "pytest-xvfb" = buildPythonPackage rec {
            pname = "pytest-xvfb";
            version = "1.0.0";
            name = "${pname}-${version}";
            src = fetchPypi {
              inherit pname version;
              sha256 = "af276c25ba1db3c25e3fd3c89663b83d05c66b960dfaf0bbde69584686b13ef5";
            };
            doCheck = false;
            propagatedBuildInputs = [
              PyVirtualDisplay
              pytest
            ];
            meta = with stdenv.lib; {
              homepage = "https://github.com/The-Compiler/pytest-xvfb";
              license = licenses.mit;
              description = "A pytest plugin to run Xvfb for tests.";
            };
          };


          "PyVirtualDisplay" = buildPythonPackage rec {
            pname = "PyVirtualDisplay";
            version = "0.2.1";
            name = "${pname}-${version}";
            src = fetchPypi {
              inherit pname version;
              sha256 = "012883851a992f9c53f0dc6a512765a95cf241bdb734af79e6bdfef95c6e9982";
            };
            doCheck = false;
            propagatedBuildInputs = [
              EasyProcess
            ];
            meta = with stdenv.lib; {
              homepage = "https://github.com/ponty/pyvirtualdisplay";
              license = licenses.bsdOriginal;
              description = "python wrapper for Xvfb, Xephyr and Xvnc";
            };
          };

          "inflection" = buildPythonPackage rec {
            pname = "inflection";
            version = "0.3.1";
            name = "${pname}-${version}";
            src = fetchPypi {
              inherit pname version;
              sha256 = "18ea7fb7a7d152853386523def08736aa8c32636b047ade55f7578c4edeb16ca";
            };
            doCheck = false;
            propagatedBuildInputs = [ ];
            meta = with stdenv.lib; {
              homepage = "http://github.com/jpvanhal/inflection";
              license = licenses.mit;
              description = "A port of Ruby on Rails inflector to Python";
            };
          };

          "faker" = buildPythonPackage rec {
            pname = "Faker";
            version = "0.7.18";
            name = "${pname}-${version}";
            src = fetchPypi {
              inherit pname version;
              sha256 = "310b20f3c497a777622920dca314d90f774028d49c7ee7ccfa96ca4b9d9bf429";
            };
            doCheck = false;
            propagatedBuildInputs = [
              dateutil
              six
            ];
            meta = with stdenv.lib; {
              homepage = "https://github.com/joke2k/faker";
              license = licenses.mit;
              description = "Faker is a Python package that generates fake data for you.";
            };
          };
        in [
          hamster-gtk
          pygobject3
        ];
    })
  ];

  # Customizable development shell setup with at last SSL certs set
  shellHook = ''
    export SSL_CERT_FILE=${cacert}/etc/ssl/certs/ca-bundle.crt
  '';
}
