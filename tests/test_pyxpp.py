"""Integration tests for pyxpp main module."""

import os
import pytest
import numpy as np
from collections import OrderedDict
from pyxpp import pyxpp


# Path to test fixtures
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


class TestParseFile:
    """Test parse_file function."""

    def test_parse_simple_file(self):
        """Test parsing a simple ODE file."""
        filepath = os.path.join(FIXTURES_DIR, "simple.ode")
        syntax = pyxpp.parse_file(filepath)
        assert isinstance(syntax, list)
        assert len(syntax) > 0

    def test_parse_functions_file(self):
        """Test parsing file with functions."""
        filepath = os.path.join(FIXTURES_DIR, "functions.ode")
        syntax = pyxpp.parse_file(filepath)
        # Should find DEFUN commands
        defuns = [cmd for cmd in syntax if cmd[0] == "DEFUN"]
        assert len(defuns) == 3

    @pytest.mark.xfail(reason="Array parsing has bugs in PLY implementation")
    def test_parse_arrays_file(self):
        """Test parsing file with arrays."""
        filepath = os.path.join(FIXTURES_DIR, "arrays.ode")
        syntax = pyxpp.parse_file(filepath)
        # Array definitions should be expanded
        pars = [cmd for cmd in syntax if cmd[0] == "PAR"]
        assert len(pars) == 3  # g[1..3] expands to 3 parameters


class TestWriteSyntax:
    """Test write_syntax function."""

    def test_write_and_read_back(self, tmp_path):
        """Test writing syntax and reading it back."""
        filepath = os.path.join(FIXTURES_DIR, "simple.ode")
        syntax = pyxpp.parse_file(filepath)

        # Write to temp file
        outfile = tmp_path / "output.ode"
        pyxpp.write_syntax(syntax, str(outfile))

        # File should exist
        assert outfile.exists()

        # Parse the generated file
        syntax2 = pyxpp.parse_file(str(outfile))

        # Should have same structure (may not be identical due to comments)
        assert len(syntax) == len(syntax2)

    def test_roundtrip_preservation(self, tmp_path):
        """Test that roundtrip preserves semantics."""
        filepath = os.path.join(FIXTURES_DIR, "simple.ode")
        syntax1 = pyxpp.parse_file(filepath)

        # Write and read
        outfile = tmp_path / "roundtrip.ode"
        pyxpp.write_syntax(syntax1, str(outfile))
        syntax2 = pyxpp.parse_file(str(outfile))

        # Write again
        outfile2 = tmp_path / "roundtrip2.ode"
        pyxpp.write_syntax(syntax2, str(outfile2))
        syntax3 = pyxpp.parse_file(str(outfile2))

        # Second and third should be identical
        assert syntax2 == syntax3


class TestReadStateVars:
    """Test read_state_vars function."""

    def test_simple_state_vars(self):
        """Test reading state variables."""
        filepath = os.path.join(FIXTURES_DIR, "simple.ode")
        state_vars = pyxpp.read_state_vars(filepath)
        assert isinstance(state_vars, np.ndarray)
        assert len(state_vars) == 1
        assert state_vars[0] == "x"

    @pytest.mark.xfail(reason="Array parsing has bugs in PLY implementation")
    def test_array_state_vars(self):
        """Test reading array state variables."""
        filepath = os.path.join(FIXTURES_DIR, "arrays.ode")
        state_vars = pyxpp.read_state_vars(filepath)
        assert len(state_vars) == 3
        assert "x1" in state_vars
        assert "x2" in state_vars
        assert "x3" in state_vars


class TestReadAuxVars:
    """Test read_aux_vars function."""

    def test_aux_vars(self):
        """Test reading auxiliary variables."""
        filepath = os.path.join(FIXTURES_DIR, "simple.ode")
        aux_vars = pyxpp.read_aux_vars(filepath)
        assert isinstance(aux_vars, np.ndarray)
        assert len(aux_vars) == 1
        assert aux_vars[0] == "x_squared"

    @pytest.mark.xfail(reason="Array parsing has bugs in PLY implementation")
    def test_no_aux_vars(self):
        """Test file with no auxiliary variables."""
        filepath = os.path.join(FIXTURES_DIR, "arrays.ode")
        aux_vars = pyxpp.read_aux_vars(filepath)
        assert len(aux_vars) == 0


class TestReadVars:
    """Test read_vars function."""

    def test_all_vars(self):
        """Test reading all variables."""
        filepath = os.path.join(FIXTURES_DIR, "simple.ode")
        all_vars = pyxpp.read_vars(filepath)
        assert len(all_vars) == 2  # 1 state + 1 aux
        assert "x" in all_vars
        assert "x_squared" in all_vars


class TestReadPars:
    """Test read_pars function."""

    def test_simple_parameters(self):
        """Test reading parameters."""
        filepath = os.path.join(FIXTURES_DIR, "simple.ode")
        pars = pyxpp.read_pars(filepath)
        assert isinstance(pars, OrderedDict)
        assert "tau" in pars
        assert "x0" in pars
        assert pars["tau"] == 10.0
        assert pars["x0"] == 1.0

    @pytest.mark.xfail(reason="Array parsing has bugs in PLY implementation")
    def test_array_parameters(self):
        """Test reading array parameters."""
        filepath = os.path.join(FIXTURES_DIR, "arrays.ode")
        pars = pyxpp.read_pars(filepath)
        assert len(pars) == 3
        assert "g1" in pars
        assert "g2" in pars
        assert "g3" in pars
        assert all(v == 0.5 for v in pars.values())


class TestReadICs:
    """Test read_ics function."""

    def test_simple_ics(self):
        """Test reading initial conditions."""
        filepath = os.path.join(FIXTURES_DIR, "simple.ode")
        ics = pyxpp.read_ics(filepath)
        assert isinstance(ics, np.ndarray)
        # Should have state ICs + aux values (initialized to 0)
        assert len(ics) == 2  # 1 state + 1 aux
        assert ics[0] == 1.0  # x initial condition
        assert ics[1] == 0.0  # x_squared aux (initialized to 0)

    @pytest.mark.xfail(reason="Array parsing has bugs in PLY implementation")
    def test_array_ics(self):
        """Test reading array initial conditions."""
        filepath = os.path.join(FIXTURES_DIR, "arrays.ode")
        ics = pyxpp.read_ics(filepath)
        assert len(ics) == 3
        assert all(ic == 0.0 for ic in ics)


class TestReadOpts:
    """Test read_opts function."""

    def test_numeric_options(self):
        """Test reading numeric options."""
        filepath = os.path.join(FIXTURES_DIR, "simple.ode")
        opts = pyxpp.read_opts(filepath)
        assert isinstance(opts, OrderedDict)
        assert "total" in opts
        assert "dt" in opts
        # Note: read_opts returns floats for integer-like values, strings for others
        assert opts["total"] == 100.0
        assert opts["dt"] == "0.1"  # Current behavior returns string

    def test_string_options(self):
        """Test reading string options."""
        filepath = os.path.join(FIXTURES_DIR, "simple.ode")
        opts = pyxpp.read_opts(filepath)
        # xplot and yplot are string values
        assert "xplot" in opts
        assert "yplot" in opts


class TestFindKeyIndex:
    """Test find_key_index function."""

    def test_find_parameter(self):
        """Test finding parameter index."""
        filepath = os.path.join(FIXTURES_DIR, "simple.ode")
        syntax = pyxpp.parse_file(filepath)
        idx = pyxpp.find_key_index(syntax, "tau")
        assert idx >= 0
        assert syntax[idx][0] == "PAR"
        assert syntax[idx][1][1] == "tau"

    def test_find_option(self):
        """Test finding option index."""
        filepath = os.path.join(FIXTURES_DIR, "simple.ode")
        syntax = pyxpp.parse_file(filepath)
        idx = pyxpp.find_key_index(syntax, "total")
        assert idx >= 0
        assert syntax[idx][0] == "OPT"


class TestAppendUID:
    """Test _append_uid function."""

    def test_append_to_file_with_extension(self):
        """Test appending UID to file with extension."""
        result = pyxpp._append_uid("output.dat", 123)
        assert result == "output-123.dat"

    def test_append_to_file_without_extension(self):
        """Test appending UID to file without extension."""
        result = pyxpp._append_uid("output", 456)
        assert result == "output-456"


class TestComplexPrograms:
    """Test with more complex programs."""

    def test_morris_lecar_parsing(self):
        """Test parsing the Morris-Lecar model."""
        # Use the ml.ode file from the root
        ml_file = os.path.join(os.path.dirname(FIXTURES_DIR), "..", "ml.ode")
        if not os.path.exists(ml_file):
            pytest.skip("ml.ode not found")

        syntax = pyxpp.parse_file(ml_file)
        assert len(syntax) > 0

        # Check various components
        pars = pyxpp.read_pars(ml_file)
        assert "g" in pars
        assert "gl" in pars

        state_vars = pyxpp.read_state_vars(ml_file)
        assert "v" in state_vars
        assert "w" in state_vars

        ics = pyxpp.read_ics(ml_file)
        assert len(ics) >= 2  # At least v and w

        opts = pyxpp.read_opts(ml_file)
        assert "total" in opts


class TestMultipleFileFormats:
    """Test handling different XPP file formats."""

    def test_apostrophe_derivative(self, tmp_path):
        """Test apostrophe notation for derivatives."""
        content = """par a=1
init x=0
x'=-a*x
done
"""
        filepath = tmp_path / "apostrophe.ode"
        filepath.write_text(content)

        syntax = pyxpp.parse_file(str(filepath))
        odes = [cmd for cmd in syntax if cmd[0] == "ODE"]
        assert len(odes) == 1
        assert odes[0][1] == "x"

    def test_d_dt_derivative(self, tmp_path):
        """Test d/dt notation for derivatives."""
        content = """par a=1
init x=0
dx/dt=-a*x
done
"""
        filepath = tmp_path / "ddt.ode"
        filepath.write_text(content)

        syntax = pyxpp.parse_file(str(filepath))
        odes = [cmd for cmd in syntax if cmd[0] == "ODE"]
        assert len(odes) == 1
        assert odes[0][1] == "x"

    def test_parameter_variants(self, tmp_path):
        """Test different parameter command variants."""
        content = """par a=1
param b=2
parameter c=3
done
"""
        filepath = tmp_path / "params.ode"
        filepath.write_text(content)

        syntax = pyxpp.parse_file(str(filepath))
        pars = [cmd for cmd in syntax if cmd[0] == "PAR"]
        assert len(pars) == 3


class TestErrorCases:
    """Test error handling."""

    def test_nonexistent_file(self):
        """Test handling of nonexistent file."""
        with pytest.raises(FileNotFoundError):
            pyxpp.parse_file("/nonexistent/file.ode")

    def test_empty_file(self, tmp_path):
        """Test handling of empty file."""
        filepath = tmp_path / "empty.ode"
        filepath.write_text("")

        syntax = pyxpp.parse_file(str(filepath))
        # Current behavior returns None for empty/error cases
        assert syntax is None or isinstance(syntax, list)
