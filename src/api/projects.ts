import { client } from './client'
import { mockGetProject, mockUpdateProject } from '../mocks/implementations'
import type {
  CreateProjectRequestDto,
  ProjectResponseDto,
  ProjectsSummaryDto,
  RoadmapProjectDto,
  UpdateProjectRequestDto,
} from './dto/project'

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

// One implementation of the current student. Rejects with NotFoundError when it doesn't exist or
// belongs to someone else, ForbiddenError without the STUDENT role.
// Mocked until project-service ships GET /api/project/projects/{id}; then:
// (await client.get<ProjectResponseDto>(`/api/project/projects/${id}`)).data
export async function getMyProject(id: number): Promise<ProjectResponseDto> {
  return mockGetProject(id)
}

// Changes the GitHub and/or deploy link of the current student's implementation; resolves with its
// full new state. Rejects with ConflictError when another implementation has that repository URL.
// Mocked until project-service ships PATCH /api/project/projects/{id}; then:
// (await client.patch<ProjectResponseDto>(`/api/project/projects/${id}`, request)).data
export async function updateMyProject(id: number, request: UpdateProjectRequestDto): Promise<ProjectResponseDto> {
  return mockUpdateProject(id, request)
}
