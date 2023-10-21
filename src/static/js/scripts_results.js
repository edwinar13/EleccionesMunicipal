

Chart.defaults.color = '#faebd7';
Chart.defaults.font.family = 'Nunito Sans';
Chart.defaults.borderColor = '#444';
Chart.defaults.font.size = '16';
Chart.defaults.font.weight = '200';

const printChart = () => {
    renderVotigChart();
}



candidates = [
    'edison beltrán',
    'juan andrés',
    'genaldo hernández',
    'jorge mikan',
    'blanca lilia',
    'voto en blanco',
]
day = ['6-Oct', '7-Oct', '8-Oct', '9-Oct', '10-Oct', '11-Oct', '12-Oct', '13-Oct', '14-Oct',
    '15-Oct', 
    '16-Oct',
    '17-Oct',
    '18-Oct',
    '19-Oct',
    '20-Oct',
    '21-Oct']

votes_day = {

    edison: [0, 5, 6, 11, 14, 14, 15, 17, 20, 20, 20, 20,20, 21, 25, 25],
    juan:   [0, 3, 7, 14, 15, 17, 23, 25, 29, 29, 30, 30,30, 33, 33, 36],
    genaldo: [0, 4, 7, 64, 87, 87, 89, 90, 92, 95, 95, 96,96, 97, 98, 100],
    mikan: [0, 3, 14, 24, 30, 34, 35, 38, 42, 42, 42, 42,42, 43, 44, 46],
    blanca: [0, 10, 22, 29, 35, 38, 38, 38, 95, 98, 98, 98,98, 100, 100, 102],
    voto_blanco: [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2,2, 3, 3, 3],
}


var ctx = document.getElementById('canvasChart').getContext('2d');


const renderVotigChart = () => {
    const data = {
        labels: day,
        datasets: [

            {
                data: votes_day.genaldo,
                borderColor: getDataColors()[2],
                backgroundColor: getDataColors('10')[2],
                tension: 0.4,
                fill: true,
                label: candidates[2],
                pointRadius: 5,
                pointHoverRadius: 10,
                pointHoverBorderWidth: 2,
                pointStyle: 'circle',
            },

            {
                data: votes_day.blanca,
                borderColor: getDataColors()[4],
                backgroundColor: getDataColors('10')[4],
                tension: 0.4,
                fill: true,
                label: candidates[4],
                pointRadius: 5,
                pointHoverRadius: 10,
                pointHoverBorderWidth: 2,
                pointStyle: 'circle',
            },
            {
                data: votes_day.mikan,
                borderColor: getDataColors()[3],
                backgroundColor: getDataColors('10')[3],
                tension: 0.4,
                fill: true,
                label: candidates[3],
                pointRadius: 5,
                pointHoverRadius: 10,
                pointHoverBorderWidth: 2,
                pointStyle: 'circle',
            },

            {
                data: votes_day.juan,
                borderColor: getDataColors()[1],
                backgroundColor: getDataColors('10')[1],
                tension: 0.4,
                fill: true,
                label: candidates[1],
                pointRadius: 5,
                pointHoverRadius: 10,
                pointHoverBorderWidth: 2,
                pointStyle: 'circle',
            },
            {
                data: votes_day.edison,
                borderColor: getDataColors()[0],
                backgroundColor: getDataColors('10')[0],
                tension: 0.4,
                fill: true,
                label: candidates[0],
                pointRadius: 5,
                pointHoverRadius: 10,
                pointHoverBorderWidth: 2,
                pointStyle: 'circle',
            },
            {
                data: votes_day.voto_blanco,
                borderColor: getDataColors()[5],
                backgroundColor: getDataColors('10')[5],
                tension: 0.4,
                fill: true,
                label: candidates[5],
                pointRadius: 5,
                pointHoverRadius: 10,
                pointHoverBorderWidth: 2,
                pointStyle: 'circle',
            },
        ]
    }
    const options = {
        maintainAspectRatio: false,
        responsive: true,
        plugins: {
            legend: {
                position: 'bottom',
            },
            title: {
                display: true,
                text: 'Intención de voto por candidato en el tiempo',
                font: {
                    size: 20,
                    weight: '100'
                },
                color: '#faebd7'
            }
        },
        interaction: {
            intersect: false,
        },
        scales: {
            x: {
                display: true,
                title: {
                    display: true
                }
            },
            y: {
                display: true,
                title: {
                    display: true,
                    text: '# de Votos acumulados',
                },
                suggestedMin: 0,
                suggestedMax: 100
            }
        }

    }




    new Chart(ctx, { type: 'line', data, options })

}


/*   FUNCIONES */
getDataColors = opacity => {
    const colors = [
        '#67cbb7',
        '#665f79',
        '#dfc963',
        '#67b56b',
        '#b98e87',
        '#ffffff', '#000000'];
    return colors.map(color => opacity ? `${color}${opacity}` : color);
}


printChart();



const percentageElements = [
    document.getElementById('percentage1'),
    document.getElementById('percentage2'),
    document.getElementById('percentage3'),
    document.getElementById('percentage4'),
    document.getElementById('percentage5'),
    document.getElementById('percentage6'),
];



const percentageValues = [33, 32, 15, 11, 8, 1];
function updatePercentage(index) {
    let currentPercentage = 0;
    const element = percentageElements[index];
    const finalPercentage = percentageValues[index];

    function animate() {
        if (currentPercentage <= finalPercentage) {
            element.textContent = currentPercentage;
            currentPercentage++;
            setTimeout(animate, 30);
        }
    }

    animate();
}


for (let i = 0; i < percentageElements.length; i++) {
    setTimeout(() => updatePercentage(i), 1200 + (i * 10));
}
