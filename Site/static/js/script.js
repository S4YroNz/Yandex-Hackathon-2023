const panel = `
<div class="panel quiz_panel" id={i}>
    <div class="panel-content">
        <input class="quiz_question" type="text" name="question{i}" placeholder="Вопрос {i}">
        <ul class="input_list">
        </ul>
        <button class="addRow" data-string="answer" data-name="question{!i!}" data-placeholder="Вариант {!j!}" form="">Добавить ответ</button>
    </div>
</div>`

const rowTypes = {
    answer: `<li class="input_list-element">
    <input class="input_list-element-text" type="text" name="question{i}_answer{j}"
    data-name="question{!i!}_answer{!j!}" data-placeholder="Вариант {!j!}"
    placeholder="Вариант {j}">
    <input class="percent_select" type="radio" name="question{i}_radio" value="{j}">
    <select class="person_select" name="question{i}_answer{j}_select" id=""></select>
    </li>`,
    person: `<li class="input_list-element">
    <input class="input_list-element-text" type="text" name="person{j}" data-name="person{!j!}" data-placeholder="Персонаж {!j!}" placeholder="Персонаж {j}">
    </li>`
}

const form = document.querySelector('form')
const createPanelButton = document.querySelector(".addPanel")

// Создание элемента из префаба
function createElementFromHTML(htmlString) {
    var div = document.createElement('div');
    div.innerHTML = htmlString.trim();
    return div.firstChild;
}

// Инициализация кнопки добавления панелей
function initAddPanelButton() {
    createPanelButton.addEventListener('click', () => {
        var newId = form.querySelectorAll('.quiz_panel').length + 1;
        var newPanel = createElementFromHTML(
            panel.replaceAll('{i}', newId)
        );
        form.insertBefore(newPanel, createPanelButton);
        init_addRow(newPanel);
        addRow(newPanel);
    })
}

// Инициализация кнопки добавления элемента
function init_addRow(panel) {
    panel.querySelector('.addRow').addEventListener('click', () => { addRow(panel) })
}

// Инициализация кнопки удаления строки
function init_deleteRow(row) {
    row.addEventListener('click', (event) => {
        if (event.target.tagName == 'LI') {
            deleteRow(row);
        }
    })
}

// Добавление елемента списка
function addRow(panel) {
    var list = panel.querySelector(".input_list");
    var rows = list.querySelectorAll("li");
    var btn = panel.querySelector('.addRow');

    var rowInd = rows.length + 1;
    var rowType = btn.getAttribute('data-string');
    var newRow = createElementFromHTML(
        rowTypes[rowType].replaceAll('{i}', panel.id).replaceAll('{j}', rowInd)
    );

    init_deleteRow(newRow);
    list.appendChild(newRow);

    if (panel.classList.contains('person_type_selected')) {
        newRow.querySelector('.input_list-element-text').addEventListener('change', (event) => {
            updateSelects(event.target.name, event.target.value);
        })
    }
    else {
        fillSelect(newRow.querySelector('select'));
        selectType(newRow);
    }
}

// Добавление вариантов в комбобоксы
function updateSelects(name, text) {
    var selects = document.querySelectorAll('.person_select');

    for (const select of selects) {
        var optionToUpdate = select.querySelector(`option[value="${name}"]`);
        optionToUpdate.innerHTML = text;
    }
}

// Добавление персонажа
function addSelectOption(input_list_element) {
    var selects = document.querySelectorAll('.person_select');
    var person = input_list_element.querySelector('.input_list-element-text');

    for (const select of selects) {
        addOption(select, person.value, person.name);
    }
}

// Удаление персонажа
function removeSelectOption(input_list_element) {
    var selects = document.querySelectorAll('.person_select');
    var person = input_list_element.querySelector('.input_list-element-text');

    for (const select of selects) {
        removeOption(select, person.name);
    }
}

// Добавление варианта в Select
function addOption(select, text, name) {
    var newOption = new Option(text, name);
    select.options[select.options.length] = newOption;
}

// Удаление варианта из Select
function removeOption(select, name) {
    for (var i = 0; i < select.options.length; i++) {
        const option = select.options[i];
        if (option.value == name) {
            select.remove(i);

            for (let j = i; j < select.options.length; j++) {
                const option = select.options[j];
                option.value = `person${j + 1}`;
            }
            return
        }
    }
}

// Наполнение Select
function fillSelect(select) {
    var persons = document.querySelector('.person_type_selected').querySelectorAll('.input_list-element-text');

    for (const person of persons) {
        addOption(select, person.value, person.name);
    }
}

// Удаление элемента списка
function deleteRow(row) {
    var list = row.parentNode;
    list.removeChild(row);
    var rows = list.querySelectorAll('.input_list-element');

    if (rows.length == 0) {
        deletePanel(list.parentNode.parentNode);
        return
    }

    for (let index = 0; index < rows.length; index++) {
        var element = rows[index];
        var input = element.querySelector('.input_list-element-text');
        input.placeholder = input.getAttribute('data-placeholder').replaceAll('{!j!}', index + 1);
        input.name = input.getAttribute('data-name').replaceAll('{!i!}', list.parentNode.parentNode.id).replaceAll('{!j!}', index + 1);
    }
}

// Удаление панели
function deletePanel(panel) {
    if (!panel.classList.contains('quiz_panel')) return;

    form.removeChild(panel);
    var panels = form.querySelectorAll('.quiz_panel');
    for (let qindex = 0; qindex < panels.length; qindex++) {
        var panel = panels[qindex];
        var num = qindex + 1
        panel.id = num;

        var question = panel.querySelector('.quiz_question');
        question.name = `question${num}`;
        question.placeholder = `Вопрос ${num}`;

        var elements = panel.querySelectorAll('.input_list-element-text');
        for (let eindex = 0; eindex < elements.length; eindex++) {
            var input = elements[eindex];
            input.name = `question${num}_answer${eindex + 1}`;
        }
    }
}

// Инициализация переключения типа Quiz'а
person_toggle = document.querySelector('.type_select').querySelector('#person')
document.querySelectorAll('.quiz_type').forEach((element) => {
    element.addEventListener('click', (event) => {
        if (person_toggle.checked) {
            document.querySelector('.person_type_selected').style.display = "flex";
            var panels = document.querySelectorAll('.quiz_panel')
            panels.forEach((panel) => {
                panel.querySelectorAll('.person_select').forEach((select) => { select.style.display = "flex" });
                panel.querySelectorAll('.percent_select').forEach((select) => { select.style.display = "none" });
            })
        }
        else {
            document.querySelector('.person_type_selected').style.display = "none";
            var panels = document.querySelectorAll('.quiz_panel')
            panels.forEach((panel) => {
                panel.querySelectorAll('.person_select').forEach((select) => { select.style.display = "none" });
                panel.querySelectorAll('.percent_select').forEach((select) => { select.style.display = "flex" });
            })
        }
    })
})
if (person_toggle.checked) {
    document.querySelector('.person_type_selected').style.display = "flex";
    var panels = document.querySelectorAll('.quiz_panel')
    panels.forEach((panel) => {
        panel.querySelectorAll('.person_select').forEach((select) => { select.style.display = "flex" });
        panel.querySelectorAll('.percent_select').forEach((select) => { select.style.display = "none" });
    })
}
else {
    document.querySelector('.person_type_selected').style.display = "none";
    var panels = document.querySelectorAll('.quiz_panel')
    panels.forEach((panel) => {
        panel.querySelectorAll('.person_select').forEach((select) => { select.style.display = "none" });
        panel.querySelectorAll('.percent_select').forEach((select) => { select.style.display = "flex" });
    })
}

// Такая же инициализация для елемента
function selectType(row) {
    if (person_toggle.checked) {
        row.querySelector('.person_select').style.display = "flex";
        row.querySelector('.percent_select').style.display = "none";
    }
    else {
        row.querySelector('.person_select').style.display = "none";
        row.querySelector('.percent_select').style.display = "flex";
    }
}

// Observer для количества пресонажей
var mutationConfig = { childList: true }
function onMutationChangeCallback(mutationConfigList) {
    for (const mutationConfig of mutationConfigList) {
        if (mutationConfig.type === 'childList') {
            if (mutationConfig.addedNodes.length) {
                console.log('added');
                addSelectOption(mutationConfig.addedNodes[0]);
            }
            else {
                console.log('removed');
                removeSelectOption(mutationConfig.removedNodes[0]);
            }
        }
    }
}
var observer = new MutationObserver(onMutationChangeCallback);
observer.observe(document.querySelector('.person_type_selected').querySelector('.input_list'), mutationConfig);

initAddPanelButton();
document.querySelectorAll('input_list-element').forEach(init_deleteRow);
document.querySelectorAll('.addRow').forEach((btn) => {
    init_addRow(btn.parentNode.parentNode);
});