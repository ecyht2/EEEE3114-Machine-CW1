openfemm(1);
opendocument('Antunes.FEM');

mi_saveas('temp.fem');

mi_modifycircprop('A', 1, 0);
mi_modifycircprop('B', 1, 0);
mi_modifycircprop('C', 1, 0);

rpm = 360/60; 
dt = 5.*10^(-6);
dtta = 2000.*rpm*dt;

coggingtorque = [];
aflux = [];
bflux = [];
cflux = [];
tt    = [];
dtta = 0.06;
n = round(120/dtta);
for(k = 0:n)
	tta = dtta*k;
	t = dt*k;
	mi_modifyboundprop('mySlidingBand', 10, tta);
	mi_analyze(1);
	mi_loadsolution();
	tq = mo_gapintegral('mySlidingBand', 0);
	tt = [tt,t];
	coggingtorque = [coggingtorque,tq];
	circpropsA=mo_getcircuitproperties('A');
	circpropsB=mo_getcircuitproperties('B');
	circpropsC=mo_getcircuitproperties('C');
	aflux = [aflux,circpropsA(3)];
	bflux = [bflux,circpropsB(3)];
	cflux = [cflux,circpropsC(3)];
	mo_close();
	if(mod(k, 100) == 0)
		fprintf('%i :: %i',k,n);
	end
end 
 
figure(1);
plot(tt,coggingtorque);
xlabel('Time, Seconds');
ylabel('Cogging Torque, N*m');
 
figure(2);
va=8*diff(aflux)/dt;
vb=8*diff(bflux)/dt;
vc=8*diff(cflux)/dt;
td=tt(2:length(tt)) - dt/2;
plot(td,va,td,vb,td,vc);
xlabel('Time, Seconds');
ylabel('Phase-to-Neutral Voltage');
 
figure(3);
vll=va-vc;
plot(td,vll);
xlabel('Time, Seconds');
ylabel('Line-to-Line Voltage');
