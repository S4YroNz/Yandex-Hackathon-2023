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
    person: `<div class="person_container">
    <li class="input_list-element">
        <input class="input_list-element-text" type="text" name="person{j}"
            data-name="person{!j!}" data-placeholder="Персонаж {!j!}"
            placeholder="Персонаж {j}">
    </li>
    <div class="input-file-group">
        <div class="preview_container hide">
            <img class="image_preview">
            <svg class="delete_image" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"
                width="50px" height="60px">
                <path
                    d="M182.746,422.305c-7.905,0-14.313-6.409-14.313-14.313v-91.604c0-7.904,6.408-14.313,14.313-14.313 c7.905,0,14.313,6.409,14.313,14.313v91.604C197.06,415.895,190.652,422.305,182.746,422.305z">
                </path>
                <path
                    d="M251.808,422.305c-7.905,0-14.313-6.409-14.313-14.313v-91.604c0-7.904,6.408-14.313,14.313-14.313 c7.905,0,14.313,6.409,14.313,14.313v91.604C266.121,415.895,259.713,422.305,251.808,422.305z">
                </path>
                <path
                    d="M320.869,422.305c-7.905,0-14.313-6.409-14.313-14.313v-91.604c0-7.904,6.408-14.313,14.313-14.313 c7.905,0,14.313,6.409,14.313,14.313v91.604C335.182,415.895,328.774,422.305,320.869,422.305z">
                </path>
                <path
                    d="M434.571,135.961c-8.435-13.251-21.524-22.423-36.856-25.828 c-7.712-1.722-15.362,3.152-17.076,10.869c-1.713,7.718,3.153,15.361,10.869,17.076c7.869,1.749,14.585,6.455,18.913,13.255 c4.328,6.8,5.75,14.879,4.002,22.748l-7.423,33.418L99.603,139.224l7.423-33.42c3.608-16.243,19.754-26.519,36.002-22.917 l145.2,32.249c7.713,1.713,15.361-3.153,17.076-10.869c1.713-7.718-3.153-15.361-10.869-17.076l-82.44-18.309l8.327-37.493 l122.96,27.308l-11.431,51.467c-1.713,7.718,3.153,15.361,10.869,17.076c1.045,0.232,2.088,0.344,3.116,0.344 c6.563,0,12.478-4.542,13.96-11.213l14.534-65.44c0.823-3.706,0.14-7.587-1.898-10.789c-2.038-3.202-5.266-5.463-8.972-6.286 L212.555,0.342c-7.713-1.709-15.362,3.152-17.076,10.869l-11.43,51.466l-34.815-7.732C117.579,47.909,86.11,67.948,79.079,99.6 l-10.526,47.391c-1.713,7.718,3.153,15.361,10.869,17.076l190.666,42.347H114.402c-7.905,0-14.313,6.409-14.313,14.313v276.96 c0,7.904,6.408,14.313,14.313,14.313h274.81c7.905,0,14.313-6.409,14.313-14.313V236.049l11.243,2.498 c1.026,0.229,2.067,0.341,3.103,0.341c2.701,0,5.37-0.764,7.686-2.239c3.202-2.038,5.463-5.266,6.288-8.972l10.526-47.391 C445.776,164.954,443.006,149.212,434.571,135.961z M374.9,483.374H128.716V235.04H374.9V483.374z">
                </path>
                </g>
            </svg>
        </div>
        <label for="personId{j}" class="input-file">
            <input class="person_image" type="file" id="personId{j}" name="person{j}_image"
                data-name="person{!j!}_image" accept=".png, .jpg, .jpeg">
            <span>
                <b id="choose">Выберите</b> <span class="dragAndDropEnabled">или
                    <b>перетащите</b></span> файл
            </span>
        </label>
        <div class="image_upload-error hide">Файл не является изображением</div>                                
    </div>
    <textarea name="person{j}_description" data-name="person{!j!}_description" placeholder="Опиасание персонажа {j}" data-placeholder="Описание персонажа {!j!}" rows="3"></textarea>
</div>`
}
const elemError = `
`

const form = document.querySelector('form')
const createPanelButton = document.querySelector(".addPanel")

// Создание элемента из префаба
function createElementFromHTML(htmlString) {
    var div = document.createElement('div')
    div.innerHTML = htmlString.trim()
    return div.firstChild
}

// Инициализация кнопки добавления панелей
function initAddPanelButton() {
    createPanelButton.addEventListener('click', () => {
        var newId = form.querySelectorAll('.quiz_panel').length + 1
        var newPanel = createElementFromHTML(
            panel.replaceAll('{i}', newId)
        )
        form.insertBefore(newPanel, createPanelButton)
        init_addRow(newPanel)
        var row = addRow(newPanel)
        console.log(row);
        row.querySelector('.percent_select').checked = true
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
            deleteRow(row)
        }
    })
}

// Добавление елемента списка
function addRow(panel) {
    var list = panel.querySelector(".input_list")
    var rows = list.querySelectorAll("li")
    var btn = panel.querySelector('.addRow')

    var rowInd = rows.length + 1
    var rowType = btn.getAttribute('data-string')
    var newRow = createElementFromHTML(
        rowTypes[rowType].replaceAll('{i}', panel.id).replaceAll('{j}', rowInd)
    )

    init_deleteRow(newRow)
    list.appendChild(newRow)

    if (panel.classList.contains('person_type_selected')) {
        newRow.querySelector('.input_list-element-text').addEventListener('change', (event) => {
            updateSelects(event.target.name, event.target.value)
        })
        initImgGroup(newRow)
    }
    else {
        fillSelect(newRow.querySelector('select'))
        selectType(newRow)
    }
    return newRow
}

// Добавление вариантов в комбобоксы
function updateSelects(name, text) {
    var selects = document.querySelectorAll('.person_select')

    for (const select of selects) {
        var optionToUpdate = select.querySelector(`option[value="${name}"]`)
        optionToUpdate.innerHTML = text
    }
}

// Добавление персонажа
function addSelectOption(input_list_element) {
    var selects = document.querySelectorAll('.person_select')
    var person = input_list_element.querySelector('.input_list-element-text')

    for (const select of selects) {
        addOption(select, person.value, person.name)
    }
}

// Удаление персонажа
function removeSelectOption(input_list_element) {
    var selects = document.querySelectorAll('.person_select')
    var person = input_list_element.querySelector('.input_list-element-text')

    for (const select of selects) {
        removeOption(select, person.name)
    }
}

// Добавление варианта в Select
function addOption(select, text, name) {
    var newOption = new Option(text, name)
    select.options[select.options.length] = newOption
}

// Удаление варианта из Select
function removeOption(select, name) {
    for (var i = 0; i < select.options.length; i++) {
        const option = select.options[i]
        if (option.value == name) {
            select.remove(i)

            for (let j = i; j < select.options.length; j++) {
                const option = select.options[j]
                option.value = `person${j + 1}`
            }
            return
        }
    }
}

// Наполнение Select
function fillSelect(select) {
    var persons = document.querySelector('.person_type_selected').querySelectorAll('.input_list-element-text')

    for (const person of persons) {
        addOption(select, person.value, person.name)
    }
}

// Удаление элемента списка
function deleteRow(row) {
    var list = row.parentNode
    console.log(list)
    console.log(row)
    list.removeChild(row)
    var panel = list.parentNode.parentNode
    var isPersonType = panel.classList.contains('person_type_selected')
    if (isPersonType){
        var rows = list.querySelectorAll('.person_container')
    } else {
        var rows = list.querySelectorAll('.input_list-element')
    }

    if (rows.length == 0) {
        deletePanel(panel)
        return
    }
    
    for (let index = 0; index < rows.length; index++) {
        var element = rows[index]
        var input = element.querySelector('.input_list-element-text')
        input.placeholder = input.getAttribute('data-placeholder').replaceAll('{!j!}', index + 1)
        input.name = input.getAttribute('data-name').replaceAll('{!i!}', panel.id).replaceAll('{!j!}', index + 1)
        console.log(panel);
        if (isPersonType){
            console.log(fileInput);
            var fileInput = element.querySelector('.person_image')
            var textarea = element.querySelector('textarea')
            fileInput.name = fileInput.getAttribute('data-name').replaceAll('{!j!}', index + 1)
            textarea.name = textarea.getAttribute('data-name').replaceAll('{!j!}', index + 1)
            textarea.placeholder = textarea.getAttribute('data-placeholder').replaceAll('{!j!}', index + 1)
            var label = element.querySelector('.input-file')
            label.setAttribute('for', `personId${index + 1}`)
            fileInput.id = `personId${index + 1}`
        } else {
            var select = element.querySelector('.person_select')
            select.name = select.getAttribute('data-name').replaceAll('{!j!}', index + 1)
        }
    }
}

// Удаление панели
function deletePanel(panel) {
    if (!panel.classList.contains('quiz_panel')) return

    form.removeChild(panel)
    var panels = form.querySelectorAll('.quiz_panel')
    for (let qindex = 0; qindex < panels.length; qindex++) {
        var panel = panels[qindex]
        var num = qindex + 1
        panel.id = num

        var question = panel.querySelector('.quiz_question')
        question.name = `question${num}`
        question.placeholder = `Вопрос ${num}`

        var elements = panel.querySelectorAll('.input_list-element-text')
        for (let eindex = 0; eindex < elements.length; eindex++) {
            var input = elements[eindex]
            input.name = select.getAttribute('data-name').replaceAll('{!i!}', qindex + 1).replaceAll('{!j!}', eindex + 1)
            var select = parent.querySelector('.person_select')
            select.name = select.getAttribute('data-name').replaceAll('{!j!}', eindex + 1)
        }
    }
}

// Инициализация переключения типа Quiz'а
person_toggle = document.querySelector('.type_select').querySelector('#person')
document.querySelectorAll('.quiz_type').forEach((element) => {
    element.addEventListener('click', (event) => {
        if (person_toggle.checked) {
            document.querySelector('.person_type_selected').style.display = "flex"
            var panels = document.querySelectorAll('.quiz_panel')
            panels.forEach((panel) => {
                panel.querySelectorAll('.person_select').forEach((select) => { select.style.display = "flex" })
                panel.querySelectorAll('.percent_select').forEach((select) => { select.style.display = "none" })
            })
        }
        else {
            document.querySelector('.person_type_selected').style.display = "none"
            var panels = document.querySelectorAll('.quiz_panel')
            panels.forEach((panel) => {
                panel.querySelectorAll('.person_select').forEach((select) => { select.style.display = "none" })
                panel.querySelectorAll('.percent_select').forEach((select) => { select.style.display = "flex" })
            })
        }
    })
})
if (person_toggle.checked) {
    document.querySelector('.person_type_selected').style.display = "flex"
    var panels = document.querySelectorAll('.quiz_panel')
    panels.forEach((panel) => {
        panel.querySelectorAll('.person_select').forEach((select) => { select.style.display = "flex" })
        panel.querySelectorAll('.percent_select').forEach((select) => { select.style.display = "none" })
    })
}
else {
    document.querySelector('.person_type_selected').style.display = "none"
    var panels = document.querySelectorAll('.quiz_panel')
    panels.forEach((panel) => {
        panel.querySelectorAll('.person_select').forEach((select) => { select.style.display = "none" })
        panel.querySelectorAll('.percent_select').forEach((select) => { select.style.display = "flex" })
    })
}

// Такая же инициализация для елемента
function selectType(row) {
    if (person_toggle.checked) {
        row.querySelector('.person_select').style.display = "flex"
        row.querySelector('.percent_select').style.display = "none"
    }
    else {
        row.querySelector('.person_select').style.display = "none"
        row.querySelector('.percent_select').style.display = "flex"
    }
}

// Observer для количества пресонажей
var mutationConfig = { childList: true }
function onMutationChangeCallback(mutationConfigList) {
    for (const mutationConfig of mutationConfigList) {
        if (mutationConfig.type === 'childList') {
            if (mutationConfig.addedNodes.length) {
                addSelectOption(mutationConfig.addedNodes[0])
            }
            else {
                removeSelectOption(mutationConfig.removedNodes[0])
            }
        }
    }
}
var observer = new MutationObserver(onMutationChangeCallback)
observer.observe(document.querySelector('.person_type_selected').querySelector('.input_list'), mutationConfig)

initAddPanelButton()
document.querySelectorAll('input_list-element').forEach(init_deleteRow)
document.querySelectorAll('.addRow').forEach((btn) => {
    init_addRow(btn.parentNode.parentNode)
})


// Загрузка файлов ~~~~~~~~~~~~~~~~~~~~~~~
function addListenerMulti(element, eventNames, listener) {
    eventNames.split(' ').forEach(e => element.addEventListener(e, listener, false))
}

function dragAndDropEnabled() {
    var div = document.createElement('div')
    return (('draggable' in div) || ('ondragstart' in div && 'ondrop' in div)) && 'FormData' in window && 'FileReader' in window
}

function preventDefaults(e) {
    e.preventDefault()
    e.stopPropagation()
}

function handleDrop(e, img_group) {
    var input = img_group.querySelector('input')
    let dt = e.dataTransfer
    input.files = dt.files
    handleFile(img_group)
}

function handleFile(img_group) {
    var input = img_group.querySelector('input')
    let file = input.files[0]
    var img_preview = img_group.querySelector('.image_preview')
    if (!validateType(file)) {
        showError(img_group)
        deleteImage(img_group)
        return
    }
    var preview_container = img_group.querySelector('.preview_container')
    preview_container.classList.remove('hide')
    img_preview.src = URL.createObjectURL(file);
}

function deleteImage(img_group) {
    var preview_container = img_group.querySelector('.preview_container')
    preview_container.classList.add('hide')
    var input = img_group.querySelector('input')
    input.files.length = 0
    input.value = ""
    var img = img_group.querySelector('.image_preview')
    img.src = ""
}

function validateType(file) {
    return [
        'jpg',
        'jpeg',
        'png',
    ].includes(file.name.split('.').pop())
}

function showError(img_group) {
    var error = img_group.querySelector('.image_upload-error')
    error.classList.remove('hide')
    setTimeout(function () { error.classList.add('hide') }, 3000)
}

function previewDroppedFile(file, img) {
    var reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onloadend = () => {
        img.src = reader.result
    }
}

function initImgGroup(img_group) {
    if (!img_group.classList.contains('input-file-group')){
        var img_group = img_group.querySelector('.input-file-group')
    }

    if (!dragAndDropEnabled()) {
        img_group.querySelectorAll('.dragAndDropEnabled').forEach((element) => {
            element.classList.add('hide')
        })
    } else {
        var input_file = img_group.querySelector('.input-file')
        addListenerMulti(input_file, "drag dragstart dragend dragover dragenter dragleave drop", (e) => {
            e.preventDefault()
            e.stopPropagation()
        })
        addListenerMulti(input_file, "dragover dragenter", (e) => {
            input_file.classList.add('hover')
        })
        addListenerMulti(input_file, "dragleave dragend drop", (e) => {
            input_file.classList.remove('hover')
        })
        input_file.addEventListener('drop', function (e) { handleDrop(e, img_group) })
        input_file.addEventListener('change', function () { handleFile(img_group) })

        var delete_image = img_group.querySelector('.delete_image')
        delete_image.addEventListener('click', () => { deleteImage(img_group) })
    }
}

document.querySelectorAll('.input-file-group').forEach(initImgGroup)

// Ингорирование :hover на мобильных устройствах
function hasTouch() {
    return 'ontouchstart' in document.documentElement
        || navigator.maxTouchPoints > 0
        || navigator.msMaxTouchPoints > 0;
}

if (hasTouch()) {
    try {
        for (var si in document.styleSheets) {
            var styleSheet = document.styleSheets[si];
            if (!styleSheet.rules) continue;

            for (var ri = styleSheet.rules.length - 1; ri >= 0; ri--) {
                if (!styleSheet.rules[ri].selectorText) continue;

                if (styleSheet.rules[ri].selectorText.match(':hover')) {
                    styleSheet.deleteRule(ri);
                }
            }
        }
    } catch (ex) { }
}