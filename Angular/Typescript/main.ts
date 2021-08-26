var minhaVar = 'minha variável';

function minhaFunc(x, y) {
    return x + y;
}

// ES6 - http://es6-features.org/#Constants
let num = 2;
const PI = 3.14;

var numeros = [1, 2, 3]
// numeros.map(function(valor) {
//     return valor * 2;
// })
numeros.map( valor => valor * 2); // ES6

class Matematica {
    soma(x, y) { 
        return x + y;
    }
}

//Decorators - https://github.com/wycats/javascript-decorators

// Tipagem de variáveis
var n1: number
