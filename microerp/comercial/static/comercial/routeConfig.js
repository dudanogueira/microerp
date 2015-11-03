angular.module("ComercialApp").config(function ($routeProvider) {
	$routeProvider.when("/", {
		templateUrl: "/static/comercial/views/home.html",
		controller: "ComercialAppCtrl",
	});
	$routeProvider.when("/preclientes", {
		templateUrl: "/static/comercial/views/pre_clientes.html",
		controller: "PreClientesCtrl",
	});
	$routeProvider.when("/precliente/:id", {
		templateUrl: "/static/comercial/views/pre_cliente_detalhe.html",
		controller: "PreClienteDetalheCtrl",
		resolve: {
			precliente: function (ComercialAPI, $route){
				return ComercialAPI.getPreCliente($route.current.params.id)
			}
		}
	});

	$routeProvider.otherwise({redirectTo: "/"});
});