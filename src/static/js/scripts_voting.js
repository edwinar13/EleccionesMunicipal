
$(document).ready(function () {

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

  $(".vote-button").click(function () {

    const candidateName = $(this).data("candidate-name");
    const candidateId = $(this).data("candidate-id");

    // Realizar la solicitud al backend con la información del voto y el token
    $.post("/votar", { candidateId: candidateId, candidateName: candidateName, token: token }, function (data) {
      // Manejar la respuesta del servidor aquí
      if (data.success) {
        if (window.history.replaceState) {
          window.history.replaceState(null, null, window.location.href);
        }
        window.location.href = "/comprobante?token=" + token;
      } else {
        alert("Error al registrar el voto.\n" + data.message);
      }
    });

  });
});



// Supongamos que estás usando jQuery para simplificar el manejo del DOM
$(document).ready(function () {
  // Manejar la respuesta de error al hacer una solicitud AJAX (por ejemplo)
  $.ajax({
    // Configuración de la solicitud AJAX
    // ...
    error: function (jqXHR) {
      if (jqXHR.status === 200) {
        // Mostrar el mensaje de alerta
        $("#alert-message").text(jqXHR.responseJSON.message);
        $("#alert-message").show();
      }
    }
  });
});



const btns = document.querySelectorAll('.btns');
const cards = document.querySelectorAll('.card-candidate');
const cardsContainer = document.querySelector('.container-candidates');

// Agrega un manejador de clic a cada card
cards.forEach(card => {
  card.addEventListener('click', () => {
    cardsContainer.classList.add('container-candidate-flex');

    console.log("adentro");
    // Remueve la clase 'expanded' de todas las cards
    cards.forEach(otherCard => {
      otherCard.classList.add('hide-card');
    });
    btns.forEach(btn => {
      btn.style.display = 'flex'
    });

    card.classList.remove('hide-card');
    card.classList.add('expanded-card');

  });
});



const cancelButtons = document.querySelectorAll('.cancel-button');
cancelButtons.forEach(cancelButton => {
  cancelButton.addEventListener('click', () => {
    event.stopPropagation();
    cardsContainer.classList.remove('container-candidate-flex');
    cards.forEach(otherCard => {
      otherCard.classList.remove('hide-card');
      otherCard.classList.remove('expanded-card');
    });
    btns.forEach(btn => {
      btn.style.display = 'none'
    });
  });
});

