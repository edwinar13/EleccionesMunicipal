const shieldRosal = document.getElementById('shield-rosal');
const shieldContainer = document.getElementById('shield-container');
const centroX = shieldContainer.offsetWidth / 2;
const centroY = shieldContainer.offsetHeight / 2;
let autoRotate = true;

shieldContainer.addEventListener('mousemove', function (event) {

    const mouseX = event.clientX - shieldContainer.getBoundingClientRect().left;
    const mouseY = event.clientY - shieldContainer.getBoundingClientRect().top;

    const deltaX = (mouseX - centroX) / centroX;
    const deltaY = (mouseY - centroY) / centroY;

    // Aplica la transformación 3D basada en la posición del mouse
    shieldRosal.style.transform = `rotateX(${-30 * deltaY}deg) rotateY(${30 * deltaX}deg)`;
});

shieldContainer.addEventListener('mouseenter', function () {
    autoRotate = false; // Detener la rotación automática al colocar el mouse sobre la imagen
});

shieldContainer.addEventListener('mouseleave', function () {
    autoRotate = true; // Reanudar la rotación automática al quitar el mouse de la imagen
});





let currentIndex = 0;
const rotations = [
    { x: 7, y: 7 },
    { x: 0, y: 10 },
    { x: -7, y: 7 },
    { x: -10, y: 0 },
    { x: -7, y: -7 },
    { x: 0, y: -10 },
    { x: 7, y: -7 },
    { x: 10, y: 0 },
];

function animate() {
    if (autoRotate) {
        const rotation = rotations[currentIndex];
        shieldRosal.style.transform = `rotateX(${rotation.x}deg) rotateY(${rotation.y}deg)`;
        currentIndex = (currentIndex + 1) % rotations.length;
        shieldRosal.style.transition = `transform ${1}.0s`;
    } else {
        shieldRosal.style.transition = `transform ${0}.8s`;
    }
}

setInterval(animate, 500);







function updateCountdown() {
    const now = new Date().getTime();
    const targetDate = new Date("2023-10-21T12:00:00").getTime(); // Fecha objetivo
    const timeRemaining = targetDate - now;

    const days = Math.floor(timeRemaining / (1000 * 60 * 60 * 24));
    const hours = Math.floor((timeRemaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((timeRemaining % (1000 * 60)) / 1000);

    updateCard("days-card", days);
    updateCard("hours-card", hours);
    updateCard("minutes-card", minutes);
    updateCard("seconds-card", seconds);
}

function updateCard(cardId, newValue) {
    const card = document.getElementById(cardId);
    const currentValue = card.querySelector("span").textContent;

    if (currentValue !== newValue.toString()) {
        // Cambia el valor y aplica el efecto de giro solo si es diferente
        card.style.transform = "rotateX(45deg)";
        setTimeout(() => {
            card.style.transform = "rotateX(0deg)";
            card.querySelector("span").textContent = newValue;
        }, 500); // Duración de la animación en milisegundos
    }
}

// Actualizar el contador cada segundo
setInterval(updateCountdown, 1000);

// Inicializar el contador
updateCountdown();


$(document).ready(function () {
    $("#poll-form button").prop("disabled", false);
    $(".loader").hide();

    // Manejar la respuesta de éxito o error al hacer una solicitud AJAX
    $("#poll-form").on("submit", function (event) {
        event.preventDefault(); // Evitar que el formulario se envíe de forma predeterminada
        $("#poll-form button").prop("disabled", true);
        $(".loader").show();

        // Agregar temporizador para desactivar el loader y habilitar el botón después de un minuto
        setTimeout(function() {
            $("#poll-form button").prop("disabled", false);
            $(".loader").hide();
        }, 10000);

        $.ajax({
            url: "/enviar_correo", // URL a la que se envía la solicitud
            method: "POST", // Método de la solicitud
            data: $(this).serialize(), // Datos del formulario serializados            
            success: function (response) {
                // Manejar la respuesta exitosa si es necesario
                // Por ejemplo, si deseas redirigir a otra página:
                // window.location.href = "/index"; 
                if (response.message) {
                    // Aplicar el estilo de alerta de éxito
                    $("#alert-message").removeClass("alert-error alert-hidden").addClass("alert-success");
                    $("#alert-message").text(response.message);
                    $("#alert-message").show();

                    $("#email-user").val("");
                    $("#poll-form button").prop("disabled", false);
                    $(".loader").hide();
                    setTimeout(function () {
                        // Ocultar la alerta
                        $("#alert-message").addClass("alert-hidden");
                    }, 6000);
                }
            },
            error: function (jqXHR) {
                if (jqXHR.status === 400 || jqXHR.status === 500) {
                    // Aplicar el estilo de alerta de error
                    $("#alert-message").removeClass("alert-success alert-hidden").addClass("alert-error");
                    $("#alert-message").text(jqXHR.responseJSON.message);
                    $("#alert-message").show();

                    // Habilitar el botón y ocultar el span de carga
                    $("#poll-form button").prop("disabled", false);
                    $(".loader").hide();

                    //$("#email-user").val("");
                    setTimeout(function () {
                        // Ocultar la alerta
                        $("#alert-message").addClass("alert-hidden");
                    }, 6000);
                }
            }
        });
    });
});

