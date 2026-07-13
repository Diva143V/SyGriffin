import { Hono } from "hono"
import { HTTPException } from "hono/http-exception"
import { describeRoute, resolver, validator } from "hono-openapi"
import z from "zod"
import { ResearchRun } from "@/science/runs/run"
import { lazy } from "@/util/lazy"

async function action<T>(body: () => Promise<T>) {
  try {
    return await body()
  } catch (error) {
    throw new HTTPException(400, { message: error instanceof Error ? error.message : String(error) })
  }
}

export const ResearchRunRoutes = lazy(() =>
  new Hono()
    .get(
      "/workflows",
      describeRoute({ summary: "List scientific workflows", operationId: "researchRun.workflows", responses: { 200: { description: "Workflow definitions" } } }),
      (c) => c.json(ResearchRun.workflows()),
    )
    .post(
      "/validate",
      describeRoute({ summary: "Validate workflow inputs", operationId: "researchRun.validate", responses: { 200: { description: "Validation preview" } } }),
      validator("json", ResearchRun.Launch),
      async (c) => c.json(await action(() => ResearchRun.validate(c.req.valid("json")))),
    )
    .get(
      "/",
      describeRoute({
        summary: "List scientific runs",
        operationId: "researchRun.list",
        responses: { 200: { description: "Project runs", content: { "application/json": { schema: resolver(ResearchRun.Info.array()) } } } },
      }),
      async (c) => c.json(await ResearchRun.list()),
    )
    .post(
      "/",
      describeRoute({
        summary: "Create a scientific run",
        operationId: "researchRun.create",
        responses: { 200: { description: "Created run", content: { "application/json": { schema: resolver(ResearchRun.Info) } } } },
      }),
      validator("json", ResearchRun.Launch),
      async (c) => c.json(await action(() => ResearchRun.create(c.req.valid("json")))),
    )
    .get(
      "/:runID",
      describeRoute({ summary: "Get a scientific run", operationId: "researchRun.get", responses: { 200: { description: "Run", content: { "application/json": { schema: resolver(ResearchRun.Info) } } } } }),
      validator("param", z.object({ runID: z.string().startsWith("run_") })),
      async (c) => c.json(await ResearchRun.get(c.req.valid("param").runID)),
    )
    .post(
      "/:runID/approve",
      describeRoute({ summary: "Approve a scientific run plan", operationId: "researchRun.approve", responses: { 200: { description: "Approved run", content: { "application/json": { schema: resolver(ResearchRun.Info) } } } } }),
      validator("param", z.object({ runID: z.string().startsWith("run_") })),
      validator("json", ResearchRun.Decision.optional()),
      async (c) => c.json(await action(() => ResearchRun.approve(c.req.valid("param").runID, c.req.valid("json")?.note))),
    )
    .post(
      "/:runID/cancel",
      describeRoute({ summary: "Cancel a scientific run", operationId: "researchRun.cancel", responses: { 200: { description: "Cancelled run", content: { "application/json": { schema: resolver(ResearchRun.Info) } } } } }),
      validator("param", z.object({ runID: z.string().startsWith("run_") })),
      async (c) => c.json(await action(() => ResearchRun.cancel(c.req.valid("param").runID))),
    )
    .post(
      "/:runID/retry",
      describeRoute({ summary: "Retry a scientific run", operationId: "researchRun.retry", responses: { 200: { description: "Reset run", content: { "application/json": { schema: resolver(ResearchRun.Info) } } } } }),
      validator("param", z.object({ runID: z.string().startsWith("run_") })),
      async (c) => c.json(await action(() => ResearchRun.retry(c.req.valid("param").runID))),
    ),
)
