import { client } from './client'
import type { ProjectsSummaryDto } from './dto/project'

// Rejects with ForbiddenError when the user has no STUDENT role.
export async function getMyProjectsSummary(): Promise<ProjectsSummaryDto> {
  const response = await client.get<ProjectsSummaryDto>('/api/project/projects/my/summary')
  return response.data
}
