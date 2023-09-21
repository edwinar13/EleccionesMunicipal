
const imagen = document.getElementById('voting-card');
const centroX = imagen.offsetWidth / 2;
const centroY = imagen.offsetHeight / 2;

imagen.addEventListener('mousemove', function(event) {
    const mouseX = event.clientX - imagen.getBoundingClientRect().left;
    const mouseY = event.clientY - imagen.getBoundingClientRect().top;

    const deltaX = (mouseX - centroX) / centroX;
    const deltaY = (mouseY - centroY) / centroY;

    // Aplica la transformación 3D basada en la posición del mouse
    imagen.style.transform = `rotateX(${-8 * deltaY}deg) rotateY(${8 * deltaX}deg)`;
});

imagen.addEventListener('mouseleave', function() {
    // Reinicia la transformación cuando el mouse sale de la imagen
    imagen.style.transform = 'rotateX(0deg) rotateY(0deg)';
});


$(document).ready(function() {
  
    // Función para extraer el valor de un parámetro de la URL
    function getParameterByName(name, url) {
      if (!url) url = window.location.href;
      name = name.replace(/[\[\]]/g, "\\$&");
      const regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
      if (!results) return null;
      if (!results[2]) return "";
      return decodeURIComponent(results[2].replace(/\+/g, " "));
    }
  
    // Obtener el token de la URL
    const token = getParameterByName("token");    
    
    // Manejar el clic en un candidato
    $(".vote-button").click(function() {
        const candidateId = $(this).data("candidate-id");
        const candidateName = $(this).data("candidate-name");
        

        let confirmationMessage = "";

        if (candidateId >= 1 && candidateId <= 4) {
            confirmationMessage = `¿Estás seguro de votar por el candidato ${candidateName}?`;
        } else if (candidateId === 5) {
            confirmationMessage = `¿Estás seguro de votar por la candidata ${candidateName}?`;
        } else if (candidateId === 6) {
            confirmationMessage = `¿Estás seguro de votar en blanco?`;
        } else {
            // Manejar otros casos si es necesario
            confirmationMessage = `¿Estás seguro de votar por este candidato?`;
        }
    
        const confirmation = confirm(confirmationMessage);
  
      if (confirmation) {
        // Obtener el ID del candidato desde el atributo de datos
        const candidateId = $(this).data("candidate-id");
  
        // Realizar la solicitud al backend con la información del voto y el token
        $.post("/votar", { candidateId: candidateId, candidateName: candidateName, token: token }, function(data) {
          // Manejar la respuesta del servidor aquí
          if (data.success) {
            alert("Voto registrado exitosamente. :)");
            if (window.history.replaceState) {
              window.history.replaceState(null, null, window.location.href);
            }
            window.location.href = "/";
          } else {
            alert("Error al registrar el voto. :(");
          }
        });
      }
    });
  });
  


  // Supongamos que estás usando jQuery para simplificar el manejo del DOM
$(document).ready(function() {
    // Manejar la respuesta de error al hacer una solicitud AJAX (por ejemplo)
    $.ajax({
        // Configuración de la solicitud AJAX
        // ...
        error: function(jqXHR) {
            if (jqXHR.status === 200) {
                // Mostrar el mensaje de alerta
                $("#alert-message").text(jqXHR.responseJSON.message);
                $("#alert-message").show();
            }
        }
    });
});



  