let icon_containers = document.querySelectorAll(".toggle-password")

const eye_open = '<i class="ph ph-eye"></i>'
const eye_closed = '<i class="ph ph-eye-slash"></i>'
const error = '<i class="ph-fill ph-x-circle"></i>'
const check = '<i class="ph-fill ph-check-fat"></i>'

icon_containers.forEach(container => {
    container.addEventListener("click", ()=>{
        const html = container.innerHTML
        if (html === eye_closed){
            container.innerHTML = eye_open
            container.previousElementSibling.type = "password"
        }else{
            container.innerHTML = eye_closed
            container.previousElementSibling.type = "text"
        }
    })
})


const form = document.querySelector("form")
const botao = document.querySelector("button")
botao.disabled = true

let passwordsMatch = false
let usuarioUnico = false


form.addEventListener("submit", (event)=>{
    event.preventDefault()
    if (passwordsMatch) form.submit()
})


const passInputs = document.querySelectorAll(".pass")
const password = passInputs[0]
const repeatPass = passInputs[1]
passInputs.forEach((element)=>{
    element.addEventListener("change", ()=>{
        if (password.value === repeatPass.value){
            password.parentElement.classList.remove('wrong')
            repeatPass.parentElement.classList.remove('wrong')
            passwordsMatch = true
        }else if (password.value && repeatPass.value){
            password.parentElement.classList.add('wrong')
            repeatPass.parentElement.classList.add('wrong')
            passwordsMatch = false
        }
        botao.disabled = !(passwordsMatch && usuarioUnico)
    })
})

const userIcon = document.querySelector(".icon")

const userField = document.querySelector("#user")
userField.addEventListener("change", (event)=>{
    botao.disabled = true
    if (userField.value == ""){
        //nao pode ficar vazio
        userField.parentElement.classList.add("wrong")
        userField.parentElement.classList.remove("right")
        userIcon.innerHTML = error
        usuarioUnico = false
        return
    }
    fetch(`/existe/${userField.value}`)
        .then(
            response => response.json()
                .then(
                    usuario => {
                        if (usuario.existe){
                            //nao pode conter usuarios duplicados
                            userField.parentElement.classList.add("wrong")
                            userField.parentElement.classList.remove("right")
                            userIcon.innerHTML = error
                            usuarioUnico = false
                        }else{
                            userField.parentElement.classList.add("right")
                            userField.parentElement.classList.remove("wrong")
                            usuarioUnico = true
                            userIcon.innerHTML = check
                        }
                        botao.disabled = !(passwordsMatch && usuarioUnico)
                    }
                )
        )
})