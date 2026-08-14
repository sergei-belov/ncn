# Task

1. Create a [Pipeline] screen based on Context. This is the screen at `/qai/projects/:project_id/pipelines/:pipeline_id`.
2. Use templates for documentation
3. Add references to spec.md


# Context
## Screen description
The screen is dran & drop vue flow screen. It has the start point from which the pipeline of Steps are follow
(For examle: create object -> open it -> change value -> delete object)


For the step and pipeline attributes you can reference tables:
[pipelines.md](../platform/tables/pipelines.md) - single pipeline info
[pre_post_pipelines.md](../platform/tables/pre_post_pipelines.md) - pipeline dependency on each other
[steps.md](../platform/tables/steps.md) - pipeline steps

# Main idea of the screen
Here user crete a test cases, where each step is some action with optional assertions.
Each step has its own attributes and can use variables (example: secrets for password, non secrets for username, project names etc.)

1. Create a table Variables at documentation
For this screen you need to create a table Variable with:
name: str
description: str
value: Any
secret: bool

2. Create a documentation for the screen