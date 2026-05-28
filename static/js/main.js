function removeRow(button) {
  const row = button.closest('tr');
  if (row) row.remove();
}

function addFactoryRow() {
  const tbody = document.querySelector('#factoriesTable tbody');
  const tr = document.createElement('tr');
  tr.innerHTML = `
    <td><input class="form-control form-control-sm mini-input" name="factory_manufacturer[]"></td>
    <td><input class="form-control form-control-sm mini-input" name="factory_product[]"></td>
    <td><input class="form-control form-control-sm mini-input" name="factory_city[]"></td>
    <td><input class="form-control form-control-sm wide-input" name="factory_address[]"></td>
    <td><input class="form-control form-control-sm mini-input" name="factory_lat[]"></td>
    <td><input class="form-control form-control-sm mini-input" name="factory_lon[]"></td>
    <td><input class="form-control form-control-sm mini-input" name="factory_distance_km[]"></td>
    <td><input class="form-control form-control-sm mini-input" name="factory_transport_time_days[]"></td>
    <td><input class="form-control form-control-sm mini-input" name="factory_weekly_quantity_units[]"></td>
    <td><input class="form-control form-control-sm mini-input" name="factory_unit_weight_kg[]"></td>
    <td><input class="form-control form-control-sm mini-input" name="factory_unit_volume_m3[]"></td>
    <td><input class="form-control form-control-sm mini-input" name="factory_manufacturer_reliability[]"></td>
    <td><input class="form-control form-control-sm mini-input" name="factory_purchase_price_per_unit[]"></td>
    <td><input class="form-control form-control-sm wide-input" name="factory_shipping_window[]"></td>
    <td><button class="btn btn-sm btn-outline-danger" type="button" onclick="removeRow(this)">×</button></td>
  `;
  tbody.appendChild(tr);
}

function addCarrierRow() {
  const tbody = document.querySelector('#carriersTable tbody');
  const tr = document.createElement('tr');
  tr.innerHTML = `
    <td><input class="form-control form-control-sm mini-input" name="carrier_name[]"></td>
    <td><input class="form-control form-control-sm mini-input" name="carrier_base_city[]"></td>
    <td><input class="form-control form-control-sm mini-input" name="carrier_cost_per_km[]"></td>
    <td><input class="form-control form-control-sm mini-input" name="carrier_reliability[]"></td>
    <td>
      <select class="form-select form-select-sm mini-input" name="carrier_tracking[]">
        <option value="true">Да</option>
        <option value="false">Нет</option>
      </select>
    </td>
    <td><input class="form-control form-control-sm mini-input" name="carrier_speed_kmh[]" value="80"></td>
    <td><button class="btn btn-sm btn-outline-danger" type="button" onclick="removeRow(this)">×</button></td>
  `;
  tbody.appendChild(tr);
}

function toggleAHPBlock() {
  const method = document.getElementById('weight_method').value;
  const block = document.getElementById('ahpBlock');
  if (!block) return;
  if (method === 'ahp') block.classList.remove('d-none');
  else block.classList.add('d-none');
}

function initYandexMap(data) {
  if (!window.ymaps || !data || !data.customer) return;

  ymaps.ready(function () {
    const customer = data.customer;
    const map = new ymaps.Map('map', {
      center: [customer.lat, customer.lon],
      zoom: 4,
      controls: ['zoomControl', 'fullscreenControl']
    });

    const customerPlacemark = new ymaps.Placemark(
      [customer.lat, customer.lon],
      { balloonContent: `<b>${customer.name}</b><br>${customer.address}` },
      { preset: 'islands#redIcon' }
    );
    map.geoObjects.add(customerPlacemark);

    data.factories.forEach(function (factory) {
      const placemark = new ymaps.Placemark(
        [factory.lat, factory.lon],
        { balloonContent: `<b>${factory.name}</b><br>${factory.product}<br>${factory.city}` },
        { preset: 'islands#blueFactoryIcon' }
      );
      map.geoObjects.add(placemark);
    });

    data.routes.forEach(function (route) {
      const multiRoute = new ymaps.multiRouter.MultiRoute({
        referencePoints: [
          [route.from_lat, route.from_lon],
          [route.to_lat, route.to_lon]
        ]
      }, { boundsAutoApply: false });
      map.geoObjects.add(multiRoute);
    });
  });
}

document.addEventListener('DOMContentLoaded', toggleAHPBlock);
