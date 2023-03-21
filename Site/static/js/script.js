var parser = new DOMParser()


function createElementFromHTML(htmlString) {
    var div = document.createElement('div');
    div.innerHTML = htmlString.trim();
    return div.firstChild;
}

const new_panel_string = `
<div class="panel">
    <div class="panel-content">
        <input class="quiz_question" type="text" name="question{i}" id="question{i}"
            placeholder="Вопрос #{i}">
        <ul class="quiz_answers">
        </ul>
        <button class="add_answer" form="">Добавить ответ</button>
    </div>
</div>`

const new_answer_string = `<li class="quiz_answer">
<input class="quiz_answer-text" type="text" name="question{i}_answer1" id="answer{j}"
    placeholder="Вариант {j}">
<select name="" id=""></select>
</li>`


// Добавление панели
var form = document.querySelector('form')
var createPanel = document.querySelector(".add_panel")
var questionId = 1;
createPanel.addEventListener('click', (event) => {
    prefab = createElementFromHTML(
        new_panel_string.replaceAll('{i}', questionId)
    );
    addAnswer(prefab.querySelector(".add_answer"));
    form.insertBefore(prefab, createPanel);
    addAnswerInit(prefab);
    questionId++;
})


// Добавление ответа на вопрос
function addAnswerInit(prefab) {
    prefab.querySelector(".add_answer").addEventListener('click', (event) => {
        addAnswer(event.target)
    })
}

document.querySelectorAll('.quiz').forEach((elem) => {
    addAnswerInit()
})

function addAnswer(btn) {
    var list = btn.parentNode.querySelector(".quiz_answers");
    var answers = list.querySelectorAll("li");
    var answerId = answers.length + 1;

    var prefab = createElementFromHTML(
        new_answer_string.replaceAll('{i}', questionId).replaceAll('{j}', answerId)
    );
    prefab.addEventListener('click', (event) => {
        if (event.target.tagName == "LI") {
            deleteAnswer(event.target);
        };
    })
    list.appendChild(prefab);
}

function deleteAnswer(answer) {
    var list = answer.parentNode;
    list.removeChild(answer);
    var answers = list.querySelectorAll(".quiz_answer");
    for (let index = 0; index < answers.length; index++) {
        const element = answers[index];
        var input = element.querySelector('.quiz_answer-text');
        input.placeholder = `Вариант ${index + 1}`;
    }
}

person_toggle = document.querySelector('.type_select').querySelector('#person')
document.querySelectorAll('.quiz_type').forEach((element) => {
    element.addEventListener('click', (event) => {
        if (person_toggle.checked) {
            document.querySelector('.person_type_selected').style.display = "flex";
        }
        else {
            document.querySelector('.person_type_selected').style.display = "none";
        }
    })
})