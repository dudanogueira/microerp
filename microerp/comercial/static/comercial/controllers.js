ComercialApp.controller('ComercialAppCtrl', function ($scope, $http) {
    $scope.app = "Comercial";
});

// LISTA PRE E CLIENTES
ComercialApp.controller('PreClientesCtrl', function ($scope, $http, $routeParams, $location) {
    $scope.app = "Comercial";
    $scope.q = $routeParams.q;
    $scope.BuscaPreClientes = function () {
        $location.search('q', $scope.q);
        // clientes
        $http.get("/comercial/api/cliente/?q="+$scope.q).success(function (data) {
            $scope.clientes = data;
        }).error(function (data, status) {
            $scope.message = "Aconteceu um problema: " + data;
        });
        // preclientes
        $http.get("/comercial/api/precliente/?q="+$scope.q).success(function (data) {
            $scope.preclientes = data;
        }).error(function (data, status) {
            $scope.message = "Aconteceu um problema: " + data;
        });
    };
    if ($scope.q){
        $scope.BuscaPreClientes()
    }
});

// DETALHE PRE CLIENTE
ComercialApp.controller('PreClienteDetalheCtrl', function ($scope, $http, precliente) {
    $scope.app = "Comercial";
    $scope.precliente = precliente.data;

});

