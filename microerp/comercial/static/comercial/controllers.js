ComercialApp.controller('ComercialAppCtrl', function ($scope, $http) {
    $scope.app = "Comercial";
});



ComercialApp.controller('PreClientesCtrl', function ($scope, $http) {
    $scope.app = "Comercial";

    var CarregarPreClientes = function () {
        $http.get("/api/v1/comercial/preclientes/").success(function (data) {
            $scope.propostas = data;
        }).error(function (data, status) {
            $scope.message = "Aconteceu um problema: " + data;
        });
    };
    CarregarPreClientes()
});

