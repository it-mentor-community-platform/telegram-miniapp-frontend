// Public interval-repetition-service DTOs. Keep the server's mixed field naming.
// Response fields follow the service's DTOs; OpenAPI omits their required lists.
export type CategoryResponseDto = {
  id: number
  name: string
  selected: boolean
  new_questions: number
  questions_ready_to_repeat: number
  all_questions: number
}

export type SpecializationResponseDto = {
  id: number
  name: string
  categories: CategoryResponseDto[]
}

export type SelectedCategoryResponseDto = {
  id: number
  name: string
  specialization: string
  new_questions: number
  questions_ready_to_repeat: number
  all_questions: number
}

export type SelectedCategoriesRequestDto = {
  // At least one category ID; this adds selections rather than replacing the set.
  categoryIds: number[]
}

export type SavedSelectedCategoryResponseDto = {
  id: number
  name: string
  specialization: string
}

export type QuestionResponseDto = {
  id: number
  title: string
  answer: string
}

export type CategoryWithQuestionsResponseDto = {
  id: number
  name: string
  specialization: string
  new_questions: number
  questions_ready_to_repeat: number
  all_questions: number
  questions: QuestionResponseDto[]
}

export type NextQuestionResponseDto = {
  questionId: number
  categoryId: number
  title: string
  answer: string
  // Available questions excluding the current one; zero still means a question was returned.
  questions_left: number
}

// SM-2 quality. Mapping the four UI choices to these values is a separate product decision.
export type ReviewQuality = 0 | 1 | 2 | 3 | 4 | 5

export type ReviewAttemptDto = {
  questionId: number
  quality: ReviewQuality
}
