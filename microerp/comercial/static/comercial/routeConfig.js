angular.module("ComercialApp").config(function ($routeProvider) {
	$routeProvider.when("/", {
		templateUrl: "/static/comercial/views/home.html",
		controller: "ComercialAppCtrl",
	});
	$routeProvider.when("/preclientes", {
		templateUrl: "/static/comercial/views/pre_clientes.html",
		controller: "PreClientesCtrl",
	});

	$routeProvider.otherwise({redirectTo: "/"});
});