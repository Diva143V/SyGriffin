class GriffinError(Exception):
    """Base exception for actionable Griffin errors."""


class InvalidVCFError(GriffinError):
    """Raised when a VCF cannot be parsed or validated."""


class InvalidHLAError(GriffinError):
    """Raised when an HLA allele does not match expected format."""


class PipelineError(GriffinError):
    """Raised when a pipeline stage fails."""
