Command-line interface
======================

The ``metaprivBIDS`` command exposes all analyses and anonymisation operations
without opening the browser GUI. Run ``metaprivBIDS --help`` to list commands
and ``metaprivBIDS COMMAND --help`` for command-specific options.

The commands are ``inspect``, ``privacy``, ``k-global``, ``k-combined``,
``round``, ``remove-decimals``, ``noise``, ``combine``, ``cig``, ``suda``, and
``metadata``. Transformations always write a new CSV or TSV file and never
overwrite the input unless that exact output path is explicitly supplied.
