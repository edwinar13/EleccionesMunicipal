const coprobantCard = document.getElementById('coprobant-card');
//const containerCard2 = document.getElementById('container-card');
const containerCard = document.getElementById('section-coprobant');
const centroX = containerCard.offsetWidth / 2;
const centroY = containerCard.offsetHeight / 2;

containerCard.addEventListener('mousemove', function(event) {
  if (window.innerWidth > 700) {
    const mouseX = event.clientX - containerCard.getBoundingClientRect().left;
    const mouseY = event.clientY - containerCard.getBoundingClientRect().top;

    const deltaX = (mouseX - centroX) / centroX;
    const deltaY = (mouseY - centroY) / centroY;
    // Aplica la transformación 3D basada en la posición del mouse
    coprobantCard.style.transform = `rotateX(${-20 * deltaY}deg) rotateY(${20 * deltaX}deg)`;
  }
});

containerCard.addEventListener('mouseleave', function() {
  // Reinicia la transformación cuando el mouse sale de la imagen
  coprobantCard.style.transform = 'rotateX(0deg) rotateY(0deg)';
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



  

const buttonCoprobant = document.getElementById('button-coprobant');
const textCoprobant = document.getElementById('text-coprobant');
const btnOff = document.getElementById('btn-off');

buttonCoprobant.addEventListener('mouseover', function() {
  textCoprobant.style.color = '#fff';
  btnOff.style.color = 'transparent';
  
});

buttonCoprobant.addEventListener('mouseleave', function() {
  textCoprobant.style.color = '#99999913';
  btnOff.style.color = '#ae2430';
});

