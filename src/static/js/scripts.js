
const imagen = document.getElementById('escudo_rosal');
const centroX = imagen.offsetWidth / 2;
const centroY = imagen.offsetHeight / 2;

imagen.addEventListener('mousemove', function(event) {
    const mouseX = event.clientX - imagen.getBoundingClientRect().left;
    const mouseY = event.clientY - imagen.getBoundingClientRect().top;

    const deltaX = (mouseX - centroX) / centroX;
    const deltaY = (mouseY - centroY) / centroY;

    // Aplica la transformación 3D basada en la posición del mouse
    imagen.style.transform = `rotateX(${-30 * deltaY}deg) rotateY(${30 * deltaX}deg)`;
});

imagen.addEventListener('mouseleave', function() {
    // Reinicia la transformación cuando el mouse sale de la imagen
    imagen.style.transform = 'rotateX(0deg) rotateY(0deg)';
});


function updateCountdown() {
    const now = new Date().getTime();
    const targetDate = new Date("2023-09-30T12:00:00").getTime(); // Fecha objetivo
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
  
  
  $(document).ready(function() {
    $("#poll-form button").prop("disabled", false);
    $(".loader").hide();

    // Manejar la respuesta de éxito o error al hacer una solicitud AJAX
    $("#poll-form").on("submit", function(event) {
        event.preventDefault(); // Evitar que el formulario se envíe de forma predeterminada
        $("#poll-form button").prop("disabled", true);
        $(".loader").show();

        $.ajax({
            url: "/enviar_correo", // URL a la que se envía la solicitud
            method: "POST", // Método de la solicitud
            data: $(this).serialize(), // Datos del formulario serializados            
            success: function(response) {
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
                    setTimeout(function() {
                        // Ocultar la alerta
                        $("#alert-message").addClass("alert-hidden");
                    }, 6000);
                }
            },
            error: function(jqXHR) {
                if (jqXHR.status === 400 || jqXHR.status === 500) {
                    // Aplicar el estilo de alerta de error
                    $("#alert-message").removeClass("alert-success alert-hidden").addClass("alert-error");
                    $("#alert-message").text(jqXHR.responseJSON.message);
                    $("#alert-message").show();
                    
                    // Habilitar el botón y ocultar el span de carga
                    $("#poll-form button").prop("disabled", false);
                    $(".loader").hide();

                    //$("#email-user").val("");
                    setTimeout(function() {
                        // Ocultar la alerta
                        $("#alert-message").addClass("alert-hidden");
                    }, 6000);
                }
            }
        });
    });
});

