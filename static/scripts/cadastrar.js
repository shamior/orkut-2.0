let icon_containers = document.querySelectorAll(".toggle-password")

const eye_open = '<i class="ph ph-eye"></i>'
const eye_closed = '<i class="ph ph-eye-slash"></i>'

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

let passwordsMatch = false


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
    })
})