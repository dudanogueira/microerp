ComercialApp.controller('ComercialAppCtrl', function ($scope, $http) {
    $scope.app = "Comercial";
});

// LISTA PRE E CLIENTES
ComercialApp.controller('PreClientesCtrl', function ($scope, $http, $routeParams, $location) {
    $scope.app = "Comercial";


    $scope.$watch('q', function (val) {
        var payload = {'q': val};
        if(val != '' && val != undefined && val.length > 2){
            $scope.carregando = true
            $http.get("/comercial/api/cliente/?q="+$scope.q).success(function (data) {
                $scope.clientes = data;
                $scope.carregando = false;
            }).error(function (data, status) {
                $scope.message = "Aconteceu um problema: " + data;
            });
            // preclientes
            $http.get("/comercial/api/precliente/?q="+$scope.q).success(function (data) {
                $scope.preclientes = data;
                $scope.carregando = false;
            }).error(function (data, status) {
                $scope.message = "Aconteceu um problema: " + data;
            });
        }else{
            $scope.preclientes = [];
            $scope.clientes = [];
        }
    });

});

// DETALHE PRE CLIENTE
ComercialApp.controller('PreClienteDetalheCtrl', function ($scope, $http, precliente) {
    $scope.app = "Comercial";
    $scope.precliente = precliente.data;

});

