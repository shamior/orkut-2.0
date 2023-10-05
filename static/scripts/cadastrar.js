const togglePasswordButtons = document.querySelectorAll(".toggle-password")


//icones do phosphor icons que o javascript vai mudar na pagina
const eye_open = '<i class="ph ph-eye"></i>'
const eye_closed = '<i class="ph ph-eye-slash"></i>'
const error = '<i class="ph-fill ph-x-circle"></i>'
const check = '<i class="ph-fill ph-check-fat"></i>'

togglePasswordButtons.forEach(container => {
    container.addEventListener("click", ()=>{
        if (container.innerHTML === eye_closed){
            container.innerHTML = eye_open
            container.previousElementSibling.type = "password"
        }else{
            container.innerHTML = eye_closed
            container.previousElementSibling.type = "text"
        }
    })
})


const submitButton = document.querySelector("button")
submitButton.disabled = true

let passwordValid = false
let usuarioUnico = false


const passInputs = document.querySelectorAll(".pass")
const [password, repeatPass] = passInputs
passInputs.forEach((element)=>{
    element.addEventListener("change", onPassChange)
})
//cada vez que algum dos campos de senha muda
//verifica se os campos estão iguais e altera o estado
//do botao e cores dos inputs
function onPassChange(event){
    let bothHaveValue = password.value && repeatPass.value
    let match = password.value === repeatPass.value
    passwordValid = match && bothHaveValue
    submitButton.disabled = !(passwordValid && usuarioUnico)
    
    if (match || !bothHaveValue){
        password.parentElement.classList.remove('wrong')
        repeatPass.parentElement.classList.remove('wrong')
        return
    }
    password.parentElement.classList.add('wrong')
    repeatPass.parentElement.classList.add('wrong')
}



const userIcon = document.querySelector(".icon")
const userField = document.querySelector("#user")
//cada vez que o campo de usuario mudar, faz uma consulta
//para o backend na rota /existe/<usuario> para ver se o
//usuario já existe no banco de dados
userField.addEventListener("change", (event)=>{
    submitButton.disabled = true
    if (userField.value == ""){
        //nao pode ficar vazio
        userField.parentElement.classList.remove("wrong")
        userField.parentElement.classList.remove("right")
        userIcon.innerHTML = ""
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
                        submitButton.disabled = !(passwordValid && usuarioUnico)
                    }
                )
        )
})