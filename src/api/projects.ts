import { client } from './client'
import type { CreateProjectRequestDto, ProjectResponseDto, ProjectsSummaryDto, RoadmapProjectDto } from './dto/project'

// Rejects with ForbiddenError when the user has no STUDENT role.
export async function getMyProjectsSummary(): Promise<ProjectsSummaryDto> {
  const response = await client.get<ProjectsSummaryDto>('/api/project/projects/my/summary')
  return response.data
}

// The current student's implementations of one roadmap project, newest first.
// Rejects with ForbiddenError when the user has no STUDENT role.
export async function getMyProjectImplementations(roadmapProject: RoadmapProjectDto): Promise<ProjectResponseDto[]> {
  const response = await client.get<ProjectResponseDto[]>('/api/project/projects/my', {
    params: { roadmap_project: roadmapProject },
  })
  return response.data
}

// Rejects with ConflictError when the repository URL is already registered as an implementation.
export async function createProject(request: CreateProjectRequestDto): Promise<ProjectResponseDto> {
  const response = await client.post<ProjectResponseDto>('/api/project/project', request)
  return response.data
}
