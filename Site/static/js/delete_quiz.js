document.querySelectorAll('.delete_quiz').forEach((element) => {
    id = element.getAttribute('data-quiz-id')
    element.href = `/deletequiz/${id}`
})