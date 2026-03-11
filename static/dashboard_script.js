// ===== PROGRAMS =====
const programs = {
    fat: {
        title: "Сжигание Жира",
        text: "Фокус на кардио тренировках и дефиците калорий."
    },
    muscle: {
        title: "Набор Мышц",
        text: "Повышенная калорийность и силовые тренировки."
    },
    endurance: {
        title: "Выносливость",
        text: "Повышение общей физической активности и дыхательных возможностей."
    }
};

function changeProgram(type) {
    document.getElementById("programTitle").textContent = programs[type].title;
    document.getElementById("programText").textContent = programs[type].text;
}


// ===== HEIGHT / WEIGHT =====
let height = 170;
let weight = 72;

function changeHeight(val) {
    height += val;
    document.getElementById("heightValue").textContent = height;
    updateBMI();
}

function changeWeight(val) {
    weight += val;
    document.getElementById("weightValue").textContent = weight;
    updateBMI();
}

function updateBMI() {
    let bmi = weight / Math.pow(height / 100, 2);
    bmi = Math.round(bmi * 10) / 10;

    document.getElementById("bmiNumber").textContent = bmi;

    let status = document.getElementById("bmiStatus");

    if (bmi < 18.5) {
        status.textContent = "Underweight";
        status.style.background = "orange";
    } else if (bmi < 25) {
        status.textContent = "You're Healthy";
        status.style.background = "green";
    } else if (bmi < 30) {
        status.textContent = "Overweight";
        status.style.background = "yellow";
    } else {
        status.textContent = "Obese";
        status.style.background = "red";
    }
}


// ===== PROTEIN / WATER / KCAL =====
let protein = 80;
let water = 102;
let kcal = 98;

function changeProtein(val) {
    protein += val;
    document.getElementById("proteinVal").textContent = protein;
}

function changeWater(val) {
    water += val;
    document.getElementById("waterVal").textContent = water;
}

function changeKcal(val) {
    kcal += val;
    document.getElementById("kcalVal").textContent = kcal;
}