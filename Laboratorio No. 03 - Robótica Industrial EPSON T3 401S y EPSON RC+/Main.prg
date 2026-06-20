Global Integer i
Global Integer j
Global Integer Ruta(40)

Function main
	Call InicializarRuta
	Motor On
	Power High
	Off DO_09 'apagar succion
	Accel 100, 100 '
	Speed 100
	Home
	
	For j = 1 To 1
		Call Paletizado
	Next

	Home
	
Fend



Function InicializarRuta

    Ruta(1) = 1
    Ruta(2) = 12
    Ruta(3) = 3
    Ruta(4) = 14
    Ruta(5) = 5
    Ruta(6) = 7
    Ruta(7) = 11
    Ruta(8) = 2
    Ruta(9) = 13
    Ruta(10) = 4
    Ruta(11) = 15
    Ruta(12) = 18
    Ruta(13) = 7
    Ruta(14) = 16
    Ruta(15) = 23
    Ruta(16) = 20
    Ruta(17) = 9
    Ruta(18) = 18
    Ruta(19) = 21
    Ruta(20) = 28
    Ruta(21) = 17
    Ruta(22) = 6
    Ruta(23) = 17
    Ruta(24) = 26
    Ruta(25) = 23
    Ruta(26) = 30
    Ruta(27) = 19
    Ruta(28) = 10
    Ruta(29) = 19
    Ruta(30) = 22
    Ruta(31) = 29
    Ruta(32) = 18
    Ruta(33) = 27
    Ruta(34) = 24
    Ruta(35) = 27
    Ruta(36) = 18
    Ruta(37) = 25
    Ruta(38) = 14
    Ruta(39) = 23
    Ruta(40) = 30

Fend




Function Paletizado

    Pallet 1, Origin, PointX, PointY, 5, 6

    For i = 1 To 39
Print Ruta(i)

        ' Huevo A
        Jump Pallet(1, Ruta(i))
        On DO_09
        Jump Pallet(1, Ruta(i + 1))
        Off DO_09

        ' Huevo B
        Jump Pallet(1, 31 - Ruta(i))
        On DO_09
        Jump Pallet(1, 31 - Ruta(i + 1))
        Off DO_09

    Next

Fend
