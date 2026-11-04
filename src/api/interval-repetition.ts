import { client } from './client'
import type {
  CategoryWithQuestionsResponseDto,
  NextQuestionResponseDto,
  ReviewAttemptDto,
  SavedSelectedCategoryResponseDto,
  SelectedCategoriesRequestDto,
  SelectedCategoryResponseDto,
  SpecializationResponseDto,
} from './dto/interval-repetition'

const basePath = '/api/interval-repetition'

// The shared client sends X-Access-Token; the gateway supplies X-Telegram-User-Id.
// List responses are arrays (confirmed by controller signatures and OpenAPI examples).
export async function getSpecializations(): Promise<SpecializationResponseDto[]> {
  const response = await client.get<SpecializationResponseDto[]>(`${basePath}/specializations`)
  return response.data
}

export async function getSelectedCategories(): Promise<SelectedCategoryResponseDto[]> {
  const response = await client.get<SelectedCategoryResponseDto[]>(`${basePath}/selected-categories`)
  return response.data
}

// Adds categories. Rejects with ConflictError for an existing selection, NotFoundError for an
// unknown category. There is no automatic retry of this mutation.
export async function saveSelectedCategories(
  request: SelectedCategoriesRequestDto,
): Promise<SavedSelectedCategoryResponseDto[]> {
  const response = await client.post<SavedSelectedCategoryResponseDto[]>(
    `${basePath}/selected-categories`,
    request,
  )
  return response.data
}

// Removes the selection, preserving question schedules and review history.
export async function deleteSelectedCategory(categoryId: number): Promise<void> {
  await client.delete(`${basePath}/selected-categories/${categoryId}`)
}

// Rejects with NotFoundError for an unknown category.
export async function getCategoryWithQuestions(categoryId: number): Promise<CategoryWithQuestionsResponseDto> {
  const response = await client.get<CategoryWithQuestionsResponseDto>(`${basePath}/categories/${categoryId}`)
  return response.data
}

// Both queues return 204 when exhausted. The common queue's OpenAPI omits this status,
// but SelectedCategoriesController explicitly returns it.
export async function getNextQuestionFromSelectedCategories(): Promise<NextQuestionResponseDto | null> {
  const response = await client.get<NextQuestionResponseDto>(`${basePath}/selected-categories/next-question`)
  return response.status === 204 ? null : response.data
}

export async function getNextQuestionFromCategory(categoryId: number): Promise<NextQuestionResponseDto | null> {
  const response = await client.get<NextQuestionResponseDto>(`${basePath}/categories/${categoryId}/next-question`)
  return response.status === 204 ? null : response.data
}

// Success is 200 with no body. Not idempotent: retrying can record another review and advance
// the schedule again. Fetch the next question only after this request succeeds.
export async function submitReviewAttempt(request: ReviewAttemptDto): Promise<void> {
  await client.post(`${basePath}/review-attempt`, request)
}
