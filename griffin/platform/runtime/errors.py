class RecipeGraphError(ValueError):
    pass


class UnknownStageDependencyError(RecipeGraphError):
    pass


class RecipeCycleError(RecipeGraphError):
    pass


class SkillResolutionError(ValueError):
    pass


class StageExecutionError(RuntimeError):
    pass


class CheckpointValidationError(ValueError):
    pass
