// Backend API: DTO types, fetch functions and the errors they reject with.
export { setAccessTokenProvider, setUnauthorizedHandler } from './client'
export { authenticateByDummy, authenticateByTelegram, parseAccessToken, type AccessToken } from './auth'
export { createProject, getMyProjectImplementations, getMyProjectsSummary } from './projects'
export {
  getSpecializations,
  getSelectedCategories,
  saveSelectedCategories,
  deleteSelectedCategory,
  getCategoryWithQuestions,
  getNextQuestionFromSelectedCategories,
  getNextQuestionFromCategory,
  submitReviewAttempt,
} from './interval-repetition'
export type {
  CategoryResponseDto,
  SpecializationResponseDto,
  SelectedCategoryResponseDto,
  SelectedCategoriesRequestDto,
  SavedSelectedCategoryResponseDto,
  QuestionResponseDto,
  CategoryWithQuestionsResponseDto,
  NextQuestionResponseDto,
  ReviewQuality,
  ReviewAttemptDto,
} from './dto/interval-repetition'
export type { DummyAuthRequestDto } from './dto/auth'
export type {
  CreateProjectRequestDto,
  ProjectResponseDto,
  ProjectsSummaryDto,
  RoadmapProjectDto,
} from './dto/project'
export type { AccessTokenClaimsDto } from './dto/token'
export type { ErrorResponseDto } from './dto/error'
export {
  ApiError,
  BadRequestError,
  ConflictError,
  ForbiddenError,
  HttpError,
  InvalidTokenError,
  NetworkError,
  NotFoundError,
  ServerError,
  UnauthorizedError,
} from './errors'
